# Entrega da documentação de matrícula em TCC I — 2026/2

**Estudante:** André Victor Xavier Pires · **Matrícula:** GRR20212735
**Ênfase:** Sistemas eletrônicos embarcados (curso noturno)
**Orientador:** Prof. Dr. Leandro dos Santos Coelho
**Coorientador:** Prof. Dr. Bruno Pohlot Ricobom — **aceite pendente de confirmação**
**Prazo interno:** enviar ao orientador até **quinta, 06/08/2026** (ele viaja na
sexta, 07/08, data em que pretende encaminhar).

---

## 1. O que precisa ser entregue

Para matrícula em **TCC I**, a regulamentação do curso exige **dois** documentos,
ambos assinados pelo orientador:

| # | Documento | Quem produz | Estado |
|---|-----------|-------------|--------|
| 1 | **Plano de trabalho** (Anexo I) | estudante | ✅ pronto — `proposta/Plano_de_Trabalho_TCC_Andre_Victor_Xavier_Pires_GRR20212735.pdf`, 11 páginas |
| 2 | **Declaração de orientação** (Anexo III) | orientador preenche e assina | ⬜ PDF original em `docs/normas-ufpr/anexo_iii_...pdf`, em branco |

O **Anexo II** (relatório final de TCC I) **não** entra agora — é o documento de
fim do semestre, para a terceira avaliação de TCC I.

> **Não confundir os dois PDFs de `proposta/`.** O que vai para a comissão é o
> **plano de trabalho** (11 páginas), que segue estritamente a lista do Anexo I.
> O `Documento_completo_com_apendices.pdf` (48 páginas, com referencial teórico,
> hipóteses, justificativa e apêndices) é material de leitura pessoal e base para
> o texto de TCC — **não é a entrega**.

---

## 2. Antes de tudo: confirmar a coorientação

O plano de trabalho **já declara o Prof. Dr. Bruno Pohlot Ricobom como
coorientador**, com os dados profissionais que o Anexo I exige. Isso pressupõe o
aceite dele. Portanto, antes de enviar:

1. **Perguntar ao Prof. Bruno** se aceita coorientar, e confirmar com ele:
   - a grafia da **titulação** e do **vínculo** (hoje: "Departamento de Engenharia
     Elétrica, Setor de Tecnologia, UFPR");
   - a **área de atuação** declarada (hoje: "instrumentação eletrônica e medição de
     campo próximo aplicada a compatibilidade eletromagnética");
   - a **contribuição** atribuída a ele (concepção das placas de teste e condução da
     validação experimental por varredura de campo próximo).
2. **Avisar o Prof. Leandro**, porque é ele quem marca a caixa de coorientação no
   Anexo III.

Se o Prof. Bruno **não** aceitar, o plano precisa ser revertido: editar
`proposta/plano/identificacao.tex` (linha do coorientador), o §1.5.1 de
`proposta/plano/conteudo.tex` e a linha `\coadvisor{...}` de `proposta/plano.tex`,
e recompilar com `make`. São cinco minutos.

---

## 3. Anexo III — o que o professor precisa preencher

O arquivo é entregue **intacto**, sem edição. Campos, na ordem em que aparecem:

- **`Eu, prof. ______`** → Leandro dos Santos Coelho
- **1ª linha de aluno** → `André Victor Xavier Pires`, matrícula `GRR20212735`
- **2ª linha de aluno** → deixar em branco (trabalho **individual**)
- **Ênfase** → marcar **`( x ) sistemas eletrônicos embarcados (curso noturno)`**
- **Coorientação** → marcar **`( x ) será coorientado por Bruno Pohlot Ricobom`**,
  coerente com o que o plano de trabalho declara
- **Data** e **assinatura** → assinatura digital pelo gov.br/SEI ou à mão com
  digitalização posterior.

---

## 4. Sequência da entrega

1. **Até qui 06/08** — enviar ao Prof. Leandro, por e-mail, dois anexos:
   - `Plano_de_Trabalho_TCC_Andre_Victor_Xavier_Pires_GRR20212735.pdf`
   - `docs/normas-ufpr/anexo_iii_declaracao_de_orientacao_de_tcc.pdf` (em branco)
2. **Orientador** — revisa o plano, preenche e assina o Anexo III, e devolve.
3. **Encaminhamento à comissão** — segue o **edital do semestre 2026/2**,
   publicado na seção específica do site do curso. Como o trabalho é individual,
   quem encaminha é o próprio estudante. (Em equipes de dois, **apenas um** aluno
   envia a documentação.)
4. **Matrícula** — a coordenação matricula na disciplina conforme o calendário
   acadêmico; o orientador é vinculado à disciplina após parecer favorável da
   comissão.
5. **Parecer da comissão** — pode conceder prazo adicional para adequação da
   documentação. **Acompanhar os editais na seção do semestre**: equipes que não
   entregam corretamente nos prazos são **reprovadas na disciplina**.

---

## 5. O que NÃO se aplica nesta etapa

O roteiro de "passo a passo para finalização do documento TCC" — transformar em
PDF, **remover metadados**, processo **SEI**, publicação no **Repositório
Institucional** — vale para o **documento final de TCC II (ou TCC DD), depois da
defesa e das correções da banca**. Nada disso entra na matrícula de TCC I.

Também não se aplica agora o **termo de aprovação**: foi dispensado pelo
colegiado do curso de Engenharia Elétrica em 01/11/2024.

---

## 6. Como este plano alimenta as avaliações do semestre

TCC I tem **três** avaliações, e todas reaproveitam o que já está escrito:

| Avaliação | Quando | O que é avaliado |
|---|---|---|
| 1ª | 8ª semana de aula | formulário preenchido pelo **orientador**; abaixo de 50 pontos = reprovação |
| 2ª | fim do semestre | **seminário perante banca**, sem documento escrito obrigatório |
| 3ª | fim do período letivo | **relatório do Anexo II**, avaliado só pelo orientador |

A rubrica sugerida para TCC I (`docs/normas-ufpr/sugestoes_avaliacao_tcc_1.pdf`) distribui 100
pontos assim — 70 de conteúdo, 30 de defesa:

| Critério | Pontos | Onde está coberto |
|---|---|---|
| Referencial teórico | **25** | ⚠️ **não está no plano** — está no cap. 2 do documento completo |
| Metodologia | **20** | plano §1.4 |
| Arguição | 20 | preparação para a banca |
| Introdução | 10 | plano §1.1 |
| Objetivos | 10 | plano §1.2 — a rubrica pontua **diferenciar geral de específicos**, o que o plano faz |
| Planejamento (cronograma) | 10 | plano §1.8 — a rubrica exige cronograma **aderente aos objetivos** |
| Apresentação | 10 | slides do seminário |

**Por isso o documento completo importa.** O plano enxuto segue só o Anexo I, que
não pede referencial teórico — mas a rubrica de TCC I dá a ele **25 pontos, o maior
peso isolado**. O capítulo 2 do `Documento_completo_com_apendices.pdf` já cobre
isso; ele é a base do relatório do Anexo II e do seminário de banca.

**Diferença entre o Anexo I (agora) e o Anexo II (dezembro):** o Anexo II
acrescenta três itens que o plano não tem — **revisão bibliográfica** (coberta pelo
documento completo), **resultados preliminares** e **potencial mercadológico do
projeto**. Vale ter isso em vista ao longo do semestre.

---

## 7. Arquivos de referência

- `docs/normas-ufpr/anexo_i_-_normas_para_plano_de_trabalho.pdf` — checklist do plano (atendido)
- `docs/normas-ufpr/anexo_ii_-_normas_para_relatorio_final_de_tcc_i.pdf` — relatório de dezembro
- `docs/normas-ufpr/anexo_iii_declaracao_de_orientacao_de_tcc.pdf` — declaração a assinar
- `docs/normas-ufpr/sugestoes_avaliacao_tcc_1.pdf` — rubrica de 100 pontos
- `proposta/README.md` — como recompilar o documento
