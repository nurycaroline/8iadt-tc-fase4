// Cliente REST do backend Node. Em dev o Vite faz proxy (ver vite.config.ts); em produção
// o dashboard é servido pelo próprio backend, então caminhos relativos funcionam nos dois casos.
import type { Caso, NovoPaciente, Paciente, ResultadoFusao } from './types'

export class ApiError extends Error {
  status: number
  constructor(status: number, mensagem: string) {
    super(mensagem)
    this.status = status
    this.name = 'ApiError'
  }
}

async function pedir<T>(url: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(url, init)
  if (!resp.ok) {
    let detalhe = resp.statusText
    try {
      const corpo = await resp.json()
      detalhe = corpo?.erro || detalhe
    } catch {
      // resposta sem JSON — mantém o statusText
    }
    throw new ApiError(resp.status, detalhe)
  }
  if (resp.status === 204) return undefined as T
  return (await resp.json()) as T
}

export const api = {
  listarPacientes: () => pedir<Paciente[]>('/pacientes'),

  criarPaciente: (dados: NovoPaciente) =>
    pedir<Paciente>('/pacientes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados),
    }),

  excluirPaciente: (id: string) => pedir<void>(`/pacientes/${id}`, { method: 'DELETE' }),

  listarCasos: () => pedir<Caso[]>('/casos'),

  obterCaso: (id: string) => pedir<Caso>(`/casos/${id}`),

  relatorioUrl: (id: string) => `/casos/${id}/relatorio`,

  // Envia o caso (multipart) e dispara a análise multimodal no backend → serviço de IA.
  analisar: (form: FormData) =>
    pedir<ResultadoFusao & { caso_id: string }>('/analisar', { method: 'POST', body: form }),
}
