import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { RiscoBadge } from '../components/RiscoBadge'
import { infoRisco } from '../risco'

describe('RiscoBadge / infoRisco', () => {
  it('mostra rótulo textual além da cor (acessibilidade)', () => {
    render(<RiscoBadge risco="ALTO" />)
    expect(screen.getByText('Alto')).toBeInTheDocument()
  })

  it('trata risco indefinido sem quebrar', () => {
    expect(infoRisco(null).rotulo).toBe('Sem análise')
    expect(infoRisco('MEDIO').classe).toBe('risco-medio')
  })
})
