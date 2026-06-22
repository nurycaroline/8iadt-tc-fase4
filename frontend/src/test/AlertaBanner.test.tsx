import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { AlertaBanner } from '../components/AlertaBanner'
import type { Alerta } from '../types'

const alerta: Alerta = {
  case_id: 'abc-123',
  risco_detectado: 'ALTO',
  mensagem_alerta: 'Sinal de infecção com febre.',
  paciente: { id: 'p1', primeiro_nome: 'Maria' },
}

describe('AlertaBanner', () => {
  it('renderiza o alerta com nome e mensagem e papel de alerta', () => {
    render(<AlertaBanner alerta={alerta} />)
    const banner = screen.getByRole('alert')
    expect(banner).toHaveTextContent('Maria')
    expect(banner).toHaveTextContent('Sinal de infecção com febre.')
  })

  it('chama onFechar ao clicar no botão de fechar', () => {
    const onFechar = vi.fn()
    render(<AlertaBanner alerta={alerta} onFechar={onFechar} />)
    fireEvent.click(screen.getByLabelText('Fechar alerta'))
    expect(onFechar).toHaveBeenCalledOnce()
  })
})
