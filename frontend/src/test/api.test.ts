import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError, api } from '../api'

afterEach(() => {
  vi.restoreAllMocks()
})

describe('api client', () => {
  it('lista casos via GET /casos', async () => {
    const casos = [{ id: 'c1', risco_detectado: 'ALTO' }]
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response(JSON.stringify(casos), { status: 200 })),
    )
    const resultado = await api.listarCasos()
    expect(resultado).toHaveLength(1)
    expect(resultado[0].id).toBe('c1')
  })

  it('lança ApiError com a mensagem do backend em erro', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response(JSON.stringify({ erro: 'caso não encontrado' }), { status: 404 })),
    )
    await expect(api.obterCaso('x')).rejects.toThrow(ApiError)
    await expect(api.obterCaso('x')).rejects.toThrow('caso não encontrado')
  })

  it('devolve undefined em 204 (exclusão)', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response(null, { status: 204 })),
    )
    await expect(api.excluirPaciente('p1')).resolves.toBeUndefined()
  })
})
