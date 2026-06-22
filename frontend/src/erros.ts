import { ApiError } from './api'

// Mensagem amigável a partir de um erro de query/mutation.
export function mensagemErro(erro: unknown): string {
  if (erro instanceof ApiError) return erro.message
  if (erro instanceof Error) return erro.message
  return 'Falha ao carregar dados'
}
