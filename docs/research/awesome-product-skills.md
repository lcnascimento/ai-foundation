# Inventário do Awesome-Product-Skills (vikast908)

Pesquisa para a issue Linear AI-59, filha do mapa AI-57 ("Plugins business e product v1"). Contexto: a ADR-0001 vendora Community skills idênticas ao Upstream; a ADR-0010 reescreve conteúdo Community em Custom skills derivadas quando o vendoring não serve; a ADR-0004 define Principles como índice mais referências. Pergunta: o que a lista [vikast908/Awesome-Product-Skills](https://github.com/vikast908/Awesome-Product-Skills) oferece de mais forte para cada documento do escopo v1 (BMC, VPC, Visão/Estratégia, Personas/ICP, JTBD, Wireframes), com licença, qualidade e se é vendorável como Community ou só base para Custom.

Pesquisado em 2026-10-10 contra o commit [`9a51b970bc7a5108ff9ff64becf1bc4d3d90aa57`](https://github.com/vikast908/Awesome-Product-Skills/tree/9a51b970bc7a5108ff9ff64becf1bc4d3d90aa57) (branch `main`). Todas as citações de arquivo se referem a esse sha. **[inferência]** marca conclusões minhas sem fonte primária.

## TL;DR

- **Não é uma lista de links.** Apesar do nome "Awesome", o repo não aponta para nenhum repositório externo: um `grep` por URLs em todos os `.md` não retorna nada. Ele contém **16 skills próprias**, uma por livro clássico de produto, cada uma com `SKILL.md` e `references/book-passages.md` (README, seções "What each skill contains" e "The skills"). Portanto não há "links promissores" a seguir, e o `deanpeters/Product-Manager-Skills` **não é citado**.
- **Repo muito jovem e sem tração**: 5 commits, todos entre 2026-07-15 e 2026-07-16 (o conteúdo inteiro entrou em `3e61ae9`), 1 estrela (GitHub API, `stargazers_count`), um único autor.
- **Cobertura do escopo v1 é fraca.** Nenhuma skill produz BMC, VPC, Personas/ICP, JTBD ou Wireframes. Só **Visão/Estratégia** tem cobertura real (`good-strategy-bad-strategy`, com apoio de `escaping-build-trap` e `empowered-product-leadership`). As demais skills são coaches de discovery, métricas, UX crítica, growth e liderança.
- **Licença: MIT no repo, mas o conteúdo central é texto de livro com copyright.** O `LICENSE` é MIT (Vikas Tiwari, 2026), porém o README diz que os `book-passages.md` são "copied word-for-word from the book", que "All rights to the original text remain with the authors and publishers", e que só "the skill scaffolding (...) is free to use and adapt" (seção "Attribution and fair use"). A MIT não pode licenciar texto de terceiros.
- **Veredito de vendoring: não vendorar nenhuma como Community.** Uma Community skill (ADR-0001) teria de levar o `book-passages.md` inteiro, redistribuindo trechos com copyright sob alegação de fair use do autor. As skills ainda se ancoram em "só ensine o que está no `book-passages.md`", então remover os trechos já tornaria a skill derivada. **[inferência]** O aproveitável é o **scaffolding** (MIT), como base de Custom skill derivada (ADR-0010), sem copiar os trechos dos livros.
- **Principle candidates**: os "anti-patterns" e "stress tests" das skills são a parte mais reutilizável. Os mais fortes para business/product: *goals are not strategy* (Rumelt), *outcomes over outputs* (Perri, Torres, Gothelf), *problem before solution / discovery before delivery* (Cagan), *evidence before copy* (Havice) e *don't blame the user* (Norman).
- **Lacunas**: BMC, VPC, Personas/ICP, JTBD e Wireframes não têm nenhuma skill. Nada no repo produz um documento persistente num formato fixo para entrar no docs backend; todas as skills produzem uma resposta de coaching de sessão.

## 1. O que o repo é

- 16 pastas de skill, cada uma com `SKILL.md` (120 a 126 linhas) e `references/book-passages.md` (49 a 79 linhas) (`wc -l` no clone).
- Todas as skills seguem um molde idêntico (README, "What each skill contains"; confirmado em cada `SKILL.md`):
  - frontmatter com só `name` e `description`;
  - "Non-negotiables": toda recomendação nomeia um princípio do livro e cita a seção; se o tema não estiver nos trechos, a skill responde "Not covered in this book's material here";
  - "Core principles (verified against extraction)", 4 a 9 por skill;
  - "Required work product" com um "practice skeleton" a preencher, mais uma lista "Never do / stop the user from";
  - formato de saída fixo: `PRINCIPLES APPLIED / FROM THE BOOK / DIAGNOSIS / IMPROVED ARTIFACT / IF YOU SKIP / NEXT 7 DAYS`;
  - um "Stress test (must not regress)": um prompt tentador e o comportamento exigido;
  - "Sibling skills" para hand-off entre livros, sem misturar frameworks.
- Cobertura honesta declarada: `dont-make-me-think` vem de um resumo de terceiros (~16k chars), não do livro (`dont-make-me-think/SKILL.md`, "Material coverage"); `finding-right-message` vem de uma extração menor (`finding-right-message/SKILL.md`, "Material coverage").
- Não há evals, testes nem CI no repo; a "verificação" descrita no README ("How the pack is kept clean") não tem ferramenta versionada (`ls` da raiz: só `LICENSE`, `README.md`, `assets/` e as 16 pastas).

## 2. Melhor fonte por documento do escopo v1

| Documento v1 | Melhor skill no repo | O que produz | Aderência |
|---|---|---|---|
| BMC | nenhuma (o mais próximo é `lean-analytics`) | "BUSINESS MODEL + STAGE", OMTM, vanity kill list (`lean-analytics/SKILL.md`) | Nula. Classifica o modelo para escolher métricas; não preenche os 9 blocos. |
| VPC | nenhuma (o mais próximo é `finding-right-message`) | VOC themes, primary promise, supports + proof, objections, CTA (`finding-right-message/SKILL.md`) | Baixa. É mensagem/copy a partir de voz do cliente; não mapeia jobs/pains/gains contra pain relievers/gain creators. Útil como insumo da evidência do lado do cliente. |
| Visão/Estratégia | `good-strategy-bad-strategy` | kernel de uma página: diagnosis com evidência, guiding policy com tradeoffs, coherent actions, cortes explícitos, proximate objective, falsifier, bad-strategy check (`good-strategy-bad-strategy/SKILL.md`, "Required work product") | Alta para estratégia. Visão em si é tratada como anti-padrão ("Vision/goal laundry lists"); a definição de visão de produto só aparece nos trechos de `empowered-product-leadership` (seção "Product Vision and Principles"). Complementos: `escaping-build-trap` (outcome statements, value exchange, Now/Next/Later com kill criteria, not-doing list). |
| Personas/ICP | nenhuma | — | Nula. "persona" e "ICP" não aparecem em nenhum `SKILL.md`; "ideal customer" aparece uma vez num trecho de Havice, ao definir value proposition. |
| JTBD | nenhuma (o mais próximo é `continuous-discovery`) | outcome, opportunity solution tree, plano de entrevistas semanais, riskiest assumption + teste (`continuous-discovery/SKILL.md`) | Baixa. "Opportunities = needs/pains/desires, not features" é vizinho de JTBD, mas não há job statements, forças do progresso nem entrevista switch. |
| Wireframes | nenhuma (o mais próximo é `dont-make-me-think` / `design-everyday-things`) | crítica: scan de 5 segundos, friction list, 3 testes de tarefa, top fixes; ou gulfs de execução/avaliação e defeitos por severidade | Baixa. Ambas **criticam** uma interface existente; nenhuma desenha wireframe. `dont-make-me-think` ainda vem de um resumo de terceiros. |

## 3. Qualidade

Pontos fortes (observados nos `SKILL.md`):

- **Disciplina anti-alucinação**: a skill só cita trechos do arquivo de referência e admite "not covered". É um bom padrão para Custom skills de business/product, que tendem a gerar conselho genérico.
- **Stress tests** concretos por skill, por exemplo "Here's our Q3 strategy: grow revenue 20%, be the market leader, delight customers" → recusar e nomear *Mistaking goals for strategy* (`good-strategy-bad-strategy/SKILL.md`). Viram casos de eval prontos para uma Custom skill.
- **Artefato obrigatório**: "advice bullets alone fail this skill".

Pontos fracos:

- **Profundidade rasa**: 4 a 9 princípios e cerca de 50 a 80 linhas de trechos por livro inteiro. O "practice skeleton" de cada skill tem 4 a 6 campos.
- **Formato de saída é de sessão de coaching** (`NEXT 7 DAYS`, role-play), não de documento. **[inferência]** Isso conflita com o modelo da ADR-0012, em que uma skill escreve um documento de um Document type no docs backend.
- **Descriptions com slash commands e listas de tópicos amplas** ("strategy, planning, priorities, roadmap"), que competiriam por roteamento com outras skills. Os slash aliases (`/good-strategy`) não funcionam como skills no Claude Code sem renomear a pasta.
- **Sem histórico, testes ou manutenção comprovada**: 1 estrela, conteúdo entregue num único commit.

## 4. Licença e vendorabilidade

- `LICENSE`: MIT, "Copyright (c) 2026 Vikas Tiwari".
- README, "Attribution and fair use": os trechos são citações curtas de livros com copyright "for the purpose of teaching and commentary"; "All rights to the original text remain with the authors and publishers"; "The skill scaffolding (the `SKILL.md` structure, the workflow, the templates, and the tooling) is free to use and adapt."
- Consequência para a ADR-0001: vendorar como Community exige copiar a pasta idêntica, incluindo `references/book-passages.md`. Esse arquivo não é coberto pela MIT, e o fair use alegado pelo autor (uso educativo, comentário) não se transfere automaticamente para a redistribuição num Marketplace. **[inferência; não é parecer jurídico]**
- Consequência para a ADR-0010: o caminho viável é uma Custom skill derivada que reaproveite só o scaffolding MIT (estrutura de non-negotiables, artefato obrigatório, anti-padrões, stress test, formato), registrando `vikast908/Awesome-Product-Skills` em `metadata.upstreams` com `sha: 9a51b970bc7a5108ff9ff64becf1bc4d3d90aa57`, `license: MIT`, e reescrevendo o conteúdo dos frameworks com palavras próprias, sem colar trechos dos livros.

| Skill | Útil para | Community? | Base para Custom? |
|---|---|---|---|
| `good-strategy-bad-strategy` | Visão/Estratégia | Não (trechos com copyright) | Sim: kernel, bad-strategy check e stress test |
| `escaping-build-trap` | Visão/Estratégia (roadmap por outcomes) | Não | Sim: value exchange e Now/Next/Later com kill criteria |
| `empowered-product-leadership` | Visão (definição de product vision) | Não | Parcial: só a ideia de "strategic context" |
| `continuous-discovery` | JTBD (vizinho) | Não | Parcial: opportunities ≠ features |
| `finding-right-message` | VPC (lado do cliente) | Não | Parcial: evidência de VOC antes da copy |
| `dont-make-me-think`, `design-everyday-things` | Wireframes (crítica) | Não | Parcial: checklist de crítica após o wireframe |
| `lean-ux` | Hipóteses e experimentos (fora do v1) | Não | Parcial: tabela de assumptions com thresholds |

## 5. Principle candidates de business/product

Extraídos das listas "Never do / stop the user from" e dos stress tests. Pela ADR-0004, um Principle aqui seria Custom (o texto do repo não é um Principle no formato upstream), escrito com palavras próprias.

1. **goals-are-not-strategy**: uma lista de metas ("crescer 20%, liderar o mercado") não é estratégia; exija diagnóstico, guiding policy e cortes explícitos (`good-strategy-bad-strategy`).
2. **outcomes-over-outputs**: sucesso é mudança de comportamento ou valor, não features entregues; aparece em três skills (`escaping-build-trap`, `continuous-discovery`, `lean-ux`), o que reforça o candidato.
3. **problem-before-solution**: não escreva PRD nem solução antes de um problem brief e dos quatro riscos (valor, usabilidade, viabilidade técnica, viabilidade de negócio) (`inspired-product-org`). Vizinho do `experience-first` já existente em `foundation`.
4. **evidence-before-copy**: sem voz do cliente, o artefato é um plano de pesquisa, não copy ou proposta de valor (`finding-right-message`). Generaliza para "não invente o cliente": personas e VPC sem evidência são hipóteses rotuladas como tal.
5. **design-not-blame**: erro do usuário é defeito de design; tooltip não é correção (`design-everyday-things`). Mais de design do que de business.

O candidato 2 é o mais transversal; os candidatos 1, 3 e 4 casam diretamente com Visão/Estratégia, VPC e Personas.

## 6. Lacunas que nenhuma skill cobre

- **BMC**: nenhuma skill preenche os 9 blocos nem verifica coerência entre eles.
- **VPC**: nenhum mapeamento customer profile (jobs/pains/gains) ↔ value map, nem checagem de fit.
- **Personas/ICP**: nenhuma; nem critério de segmento, nem proto-persona, nem anti-persona.
- **JTBD**: nenhuma; sem job statement, forças do progresso, entrevista switch ou outcome-driven innovation.
- **Wireframes**: nenhuma skill gera wireframe ou fluxo; só crítica de interface pronta.
- **Visão** como documento: há estratégia (kernel), mas não um documento de visão de produto (horizonte, narrativa, princípios de produto).
- **Transversal**: nenhuma skill escreve um documento persistente num formato fixo; todas devolvem uma sessão de coaching. Os Document types de business/product (ADR-0012 permite que um Domain plugin os adicione) teriam de ser desenhados do zero.

## Fontes

- Repo e README: https://github.com/vikast908/Awesome-Product-Skills/blob/9a51b970bc7a5108ff9ff64becf1bc4d3d90aa57/README.md
- LICENSE: https://github.com/vikast908/Awesome-Product-Skills/blob/9a51b970bc7a5108ff9ff64becf1bc4d3d90aa57/LICENSE
- Skills lidas (no mesmo sha): `good-strategy-bad-strategy`, `inspired-product-org`, `escaping-build-trap`, `empowered-product-leadership`, `continuous-discovery`, `finding-right-message`, `lean-ux`, `dont-make-me-think`, `design-everyday-things`, `lean-analytics` (os `SKILL.md`; `book-passages.md` amostrados por `grep` e lido em parte o de `good-strategy-bad-strategy`).
- Metadados: GitHub API `repos/vikast908/Awesome-Product-Skills` (licença MIT, 1 estrela, último push 2026-07-15T19:56:14Z) e `git log` do clone (5 commits).
