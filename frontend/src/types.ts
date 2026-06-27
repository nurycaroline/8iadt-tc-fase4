// Tipos espelhando o contrato de API (docs/contrato-api.md) e as respostas do backend Node.

export type Risco = 'BAIXO' | 'MEDIO' | 'ALTO'

export interface Paciente {
  id: string
  primeiro_nome: string
  idade: number | null
  gestante: boolean
  idade_gestacional_semanas: number | null
  criado_em?: string
}

// Subevidência binária dos classificadores ML da Fase 8 (depressão/violência).
export interface SubEvidencia {
  rotulo?: string
  confianca?: number
}

// Evidência de texto unificada (Fase 8): achado por keywords + sinais ML de depressão/violência.
export interface EvidenciaTexto {
  achado?: string
  trecho?: string
  depressao?: SubEvidencia | null
  violencia?: SubEvidencia | null
}

export interface Evidencias {
  video_cicatriz?: { evento?: string; confianca?: number } | null
  video_fisioterapia?: { execucao?: string; amplitude?: string } | null
  sinais_vitais?: { tipo?: string; valor?: string } | null
  // Áudio na Fase 8: análise dupla (acústico + transcrição→texto). `categoria`/`confianca`
  // são campos legados derivados, mantidos por compatibilidade.
  audio?: {
    acustico?: SubEvidencia | null
    transcricao?: string
    texto?: EvidenciaTexto | null
    categoria?: string
    confianca?: number
  } | null
  texto?: EvidenciaTexto | null
}

export interface ResultadoFusao {
  timestamp?: string
  case_id?: string
  risco_detectado: Risco
  evidencias?: Evidencias
  mensagem_alerta?: string
  relatorio_url?: string | null
}

export interface Caso {
  id: string
  paciente_id: string
  video_cicatriz_url: string | null
  video_fisioterapia_url: string | null
  audio_url: string | null
  sinais_vitais_csv_url: string | null
  texto_clinico: string | null
  risco_detectado: Risco | null
  relatorio_url: string | null
  resultado_json: ResultadoFusao | null
  timestamp: string
  paciente?: Paciente
}

export interface Alerta {
  case_id: string
  risco_detectado: Risco
  mensagem_alerta?: string
  relatorio_url?: string | null
  paciente?: { id: string; primeiro_nome: string } | null
  timestamp?: string
}

export interface NovoPaciente {
  primeiro_nome: string
  idade: number | null
  gestante: boolean
  idade_gestacional_semanas: number | null
}
