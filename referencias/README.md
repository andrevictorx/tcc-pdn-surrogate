# Acervo de referências

Cópias locais das obras citadas em [`../proposta/referencias.bib`](../proposta/referencias.bib).

> ⚠️ **Nenhum arquivo desta pasta é versionado.** São obras de terceiros protegidas
> por direito autoral e folhas de dados sob os termos de uso da TUHH; o `.gitignore`
> as exclui do repositório público. Só este índice é versionado.

## `livros/`

| Arquivo | Chave BibTeX | Referência |
|---|---|---|
| `ELECTROMAGNETIC COMPATIBILITY ENGINEERING.pdf` | `ott2009` | OTT, H. W. *Electromagnetic Compatibility Engineering*. Hoboken: John Wiley & Sons, 2009. ISBN 978-0-470-18930-6 |
| `high-speed-digital-design.pdf` | `johnson1993` | JOHNSON, H. W.; GRAHAM, M. *High-Speed Digital Design: A Handbook of Black Magic*. Upper Saddle River: Prentice Hall, 1993. ISBN 0-13-395724-1 |
| `Signal and Power Integrity - Simplified_2nd_...pdf` | `bogatin2010` | BOGATIN, E. *Signal and Power Integrity — Simplified*. 2. ed. Upper Saddle River: Prentice Hall, 2010. ISBN 978-0-13-234979-6 |
| `Surrogate Model-Based Engineering Design and Optimization.pdf` | `jiang2020` | JIANG, P.; ZHOU, Q.; SHAO, X. *Surrogate Model-Based Engineering Design and Optimization*. Singapore: Springer Nature, 2020. doi:10.1007/978-981-15-0731-1 |
| *(pendente)* | `geron2022` | GÉRON, A. *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow*. 3. ed. Sebastopol: O'Reilly, 2022. ISBN 978-1-098-12597-4 |

## `artigos/`

PDFs de artigos consultados. Os registros bibliográficos completos, com DOI, estão
no `.bib`; os DOIs foram conferidos via Crossref.

## `datasheets-si-pi/`

Folhas de dados dos subconjuntos da SI/PI-Database (TUHH). São a fonte primária dos
números de configurações, portas, cavidades e faixa de frequência citados na
Seção 1.4 do plano de trabalho. Distribuição a terceiros é vedada pelos termos de
uso da base — ver <https://www.tet.tuhh.de/en/si-pi-database/>.

## Procedimento de verificação

Todos os registros do `.bib` foram conferidos na fonte primária em 05/08/2026:

- **artigos e o livro da Springer** — API do Crossref, pelo DOI;
- **livros sem DOI** — catálogo da Open Library, pelo ISBN, e página de copyright do
  próprio exemplar nesta pasta;
- **normas IEC/CISPR** — catálogo oficial em <https://webstore.iec.ch>, incluindo
  conferência da edição vigente.

Reproduzir a conferência dos DOIs:

```bash
curl -s "https://api.crossref.org/works/10.1109/ACCESS.2021.3061788" | python3 -m json.tool
```
