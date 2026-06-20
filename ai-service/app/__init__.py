"""Serviço de IA (Fase 2) — modelos individuais por modalidade.

Cada subpacote de modalidade (``sinais_vitais``, ``cicatriz``, ``fisioterapia``, ``audio``,
``texto``) expõe uma função de inferência que devolve o **dicionário de evidência padronizado**
do contrato de API (docs/contrato-api.md §3), pronto para o motor de fusão da Fase 3.
"""
