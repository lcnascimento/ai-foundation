# Inventário do Product-Manager-Skills (deanpeters)

Pesquisa da issue Linear AI-58, filha do mapa AI-57 ("Plugins business e product v1"). Pergunta: o que [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills) oferece para os documentos do escopo v1 (BMC, VPC, Visão/Estratégia, Personas/ICP, JTBD, Wireframes), se dá para vendorar como Community skill ou só serve de base para Custom (ADR-0001, ADR-0010), que candidatos a Principle existem e que skills fora do escopo justificariam trocar um documento.

Fonte lida: clone raso do repositório no commit [`1b5a524`](https://github.com/deanpeters/Product-Manager-Skills/tree/1b5a524ebb95e9497fa3f25002d8b8ec528d4444) (2026-09-01), lido em 2026-10-10. Os caminhos citados abaixo são relativos a esse commit. **[inferência]** marca uma conclusão minha que não está escrita na fonte.

## TL;DR

- **Licença CC BY-NC-SA 4.0 para tudo** (`LICENSE`, `README.md` §License: "There is no mix of licenses here"). O ShareAlike obriga qualquer adaptação a sair sob a mesma licença, e o NonCommercial proíbe revender. Os plugins do Marketplace são MIT (`plugins/*/.claude-plugin/plugin.json`). Uma skill derivada (ADR-0010) teria de ser CC BY-NC-SA, não MIT. **[inferência]**
- **Cobertura do escopo v1 é parcial.** Não há skill de BMC, de VPC completo, de visão de produto, de ICP nem de wireframes. Há JTBD (que é, na prática, o perfil do cliente do VPC), proto-persona, positioning statement/workshop (o mais próximo de "visão") e storyboard (narrativa, explicitamente "not a UI mockup").
- **Vendorável como Community é possível, mas ruim de encaixar.** As skills têm 250 a 575 linhas, são escritas para ensinar o PM ("ABC — Always Be Coaching", `AGENTS.md`) e se referenciam em cadeia (`skills/<x>/SKILL.md`), então vendorar uma puxa várias (ADR-0001). Melhor uso: **base de leitura para Custom skills** escritas a partir dos frameworks públicos (Christensen, Osterwalder, Moore), não do texto do Dean, o que evita herdar o ShareAlike. **[inferência]**
- **Candidatos a Principle:** "Fact / Inference / Assumption" (rotular cada afirmação), "Research without a decision is a hobby" e "Use the cheapest prototype that tells the harshest truth" (PoL probe). "Proto, não validado" (persona como hipótese) é mais fraco.
- **Trocas sugeridas:** Wireframes → `pol-probe` (escolher o protótipo mais barato que testa a hipótese) ou storyboard; Visão/Estratégia → positioning statement (Moore) como núcleo; BMC poderia dar lugar a `lean-ux-canvas` ou `tam-sam-som-calculator` se o foco for produto e não modelo de negócio.

## 1. Estrutura do repositório

- 77 pastas em `skills/`, cada uma com `SKILL.md` e, na maioria, `template.md` e `examples/` (`sample.md` e, em várias, `sample-industrial.md`). Duas têm `scripts/` (`tam-sam-som-calculator/scripts/market-sizing.py`, `user-story/scripts/`). Nenhuma usa `references/`.
- Frontmatter: `name`, `description` (≤ 200 caracteres), `intent`, `type` (`component`, `interactive` ou `workflow`), `theme`, `best_for`, `scenarios`, `estimated_time`. Sem `license` (`AGENTS.md` §Coding Style; ex.: `skills/jobs-to-be-done/SKILL.md` linhas 1-17).
- Seções fixas em todo `SKILL.md`: Purpose, Input, Key Concepts, Application, Examples, Common Pitfalls, References (`AGENTS.md` §Coding Style).
- Skills `interactive` delegam o protocolo de conversa a `workshop-facilitation` (uma pergunta por vez, opções numeradas, rótulos de progresso), declarado na seção "Facilitation Source of Truth" (ex.: `skills/positioning-workshop/SKILL.md` linhas 73-84).
- Skills de investigação seguem o contrato `autonomous-investigation` (orçamento de perguntas, gate de plano de busca, rótulos de evidência, saída estável) (`skills/autonomous-investigation/SKILL.md` §The contract).
- Filosofia declarada: "Pedagogic and Practical in Equal Measure", "**ABC — Always Be Coaching**", "Do not optimize for brevity at the cost of explanation", "Anti-patterns are load-bearing" (`AGENTS.md` linhas 3-20).
- Muitas skills dizem "Adapted from `prompts/<x>.md` in [product-manager-prompts]", repositório do mesmo autor e mesma licença (`README.md` linha 298).

## 2. Licença e vendorabilidade

- `LICENSE`: Attribution-NonCommercial-ShareAlike 4.0 International. `README.md` linhas 292-306: vale para "every skill, template, and doc". Uso no trabalho em empresa com fins lucrativos é permitido; "Adapt and remix them — share what you build under this same license, with credit"; "Don't sell them — no repackaging the skills themselves into a paid product, course, or service without expressed written permission".
- Consequências para o Marketplace **[inferência]**:
  - **Vendorar como Community (ADR-0001)**: viável juridicamente para uso interno, com `license: CC-BY-NC-SA-4.0` no frontmatter e o `LICENSE` copiado ao lado. Mas o plugin declara `"license": "MIT"`, então passaria a ter conteúdo com licença mista, e precisaria registrar isso.
  - **Derivar uma Custom skill (ADR-0010) a partir do texto**: a cópia reescrita é material adaptado, e o SA obriga a sair sob CC BY-NC-SA. Isso conflita com o plugin MIT.
  - **Escrever Custom a partir dos frameworks públicos** (JTBD de Christensen/Ulwick, VPC de Osterwalder, positioning de Moore, Lean UX Canvas de Gothelf), usando o repositório só como leitura: frameworks e ideias não são protegidos por direito autoral, só o texto. É a via que mantém MIT, desde que não se copie texto, exemplos nem templates.
- Encaixe técnico com ADR-0001 e ADR-0010 **[inferência]**:
  - As cadeias de dependência são longas. `positioning-workshop` usa `workshop-facilitation` e `positioning-statement` e referencia `proto-persona`, `jobs-to-be-done` e `problem-statement` (`skills/positioning-workshop/SKILL.md` linha 438). `product-strategy-session` "Orchestrates 15+ component and interactive skills" (linha 447). Pela ADR-0001, vendorar uma skill vendora as que ela invoca.
  - As referências usam caminhos do repositório (`skills/proto-persona/SKILL.md`), que não resolvem no layout `plugins/<plugin>/skills/` sem editar, e editar torna a skill derivada.
  - O estilo ABC (ensinar o humano, anti-padrões extensos, 250-575 linhas por skill) vai contra o critério da ADR-0010 ("A line survives the rewrite only if it changes the model's default behaviour") e contra a preferência do mapa por poucas skills focadas.

## 3. Cobertura do escopo v1

| Documento v1 | Skill(s) no repositório | Cobertura |
|---|---|---|
| Business Model Canvas | nenhuma | Ausente. O BMC só aparece citado como lente dentro de `competitive-analysis-process` (linhas 62 e 112). Não há skill que o produza, nem "Lean Canvas". |
| Value Proposition Canvas | `jobs-to-be-done` | Metade: jobs/pains/gains (perfil do cliente). Falta o mapa de valor (produtos e serviços, pain relievers, gain creators) e o fit. |
| Visão / Estratégia | `positioning-statement`, `positioning-workshop`, `product-strategy-session` | Parcial: posicionamento (Moore) e um workflow de 4 semanas. Não há documento de visão (horizonte, north star, princípios de produto). |
| Personas / ICP | `proto-persona` | Persona sim. ICP só aparece como critério dentro de `acquisition-channel-advisor` e como fonte de dados em `intelligence-collection-disciplines`. |
| JTBD | `jobs-to-be-done` | Boa, mas no formato Osterwalder (jobs/pains/gains), não job statements de Ulwick/ODI nem forças do progresso. |
| Wireframes | nenhuma (`storyboard`, `pol-probe` adjacentes) | Ausente. "Wireframes" só aparece como seção opcional do `prd-development` (template linha 350). `storyboard` diz "This is not a UI mockup" (linha 23). |

### 3.1 `jobs-to-be-done` (component, 391 linhas + template 65 + 2 exemplos)

- Produz: um documento de jobs funcionais, sociais e emocionais; dores (challenges, costliness, common mistakes, unresolved problems); ganhos (expectations, savings, adoption factors, life improvement); priorização por intensidade.
- Declara a origem: "Influenced by Clayton Christensen and the Value Proposition Canvas (Osterwalder)" (linha 39). É, na prática, o lado do cliente do VPC.
- Qualidade: boas verificações ("Verb-driven", "Solution-agnostic"), anti-padrões úteis ("Not a feature wishlist", "Not demographics") e pitfalls ("Fabricating JTBD Without Research"). Pontos fracos: muito texto que o modelo já sabe (perguntas óbvias por subseção), sem job statement no formato "When… I want to… so I can…", e um placeholder solto em References ("[Link to relevant Dean Peters' Substack articles if applicable]", linha 381).
- Veredito **[inferência]**: boa base de leitura para um Document type `jtbd` ou para fundir JTBD no VPC. A Custom precisaria do mapa de valor e de job statements.

### 3.2 `proto-persona` (component, 347 linhas + template 45 + 2 exemplos)

- Produz: persona com nome aliterativo, bio e demografia, citações, dores, o que tenta realizar, objetivos, autoridade de decisão, influenciadores e crenças, mais um passo de validação.
- Conceito central: persona como hipótese ("This is not a validated persona—it's a 'proto' (prototype) persona", linha 22), com tabela proto vs. validada.
- Qualidade: os pitfalls são bons ("Demographics Without Behavior", "Creating 10 Proto-Personas", "Fabricating Quotes"). Não cobre ICP B2B (firmografia, gatilhos de compra, critérios de desqualificação).
- Veredito **[inferência]**: base razoável para Personas. ICP teria de vir de outra fonte.

### 3.3 `positioning-statement` (component, 242 linhas) e `positioning-workshop` (interactive, 438 linhas)

- Produzem o statement de Geoffrey Moore: "For [target] that need [need], [product] is a [category] that [benefit]. Unlike [alternative], [product] provides [differentiation]" (`skills/positioning-statement/template.md`). O workshop faz 5 perguntas, uma por vez, e gera o mesmo artefato com resumo de uma frase.
- Qualidade: compacto e útil, com pitfalls sólidos ("For Everyone", "Imaginary Competitor", "Differentiation Without Proof"). O workshop depende de `workshop-facilitation`.
- Veredito **[inferência]**: é o que o repositório tem de mais próximo de "Visão". Serve de núcleo de um documento de Visão/Estratégia, mas sozinho não é visão.

### 3.4 `product-strategy-session` (workflow, 447 linhas)

- Orquestra 6 fases ao longo de cerca de 4 semanas (posicionamento → problema → solução → roadmap → alinhamento → execução), com pontos de decisão entre as fases (linhas 85-290).
- Veredito **[inferência]**: é um processo, não um documento. Não serve como skill de um plugin enxuto. O valor está nos pontos de decisão ("Do we have enough customer context?") como ideia para encadear documentos, que é uma das perguntas abertas do mapa.

### 3.5 `storyboard` (component, 273 linhas)

- Produz uma narrativa de 6 quadros (personagem, problema, "oh crap", solução, "aha", vida depois) com descrição visual de cada quadro e sugestão de DALL·E/MidJourney (linhas 38-46, 141-175).
- Veredito **[inferência]**: não substitui wireframe. Pode ser alternativa a Wireframes se o objetivo for alinhar a proposta com humanos, não especificar interface.

### 3.6 Adjacentes relevantes

- `lean-ux-canvas` (interactive, 575 linhas): Lean UX Canvas v2 de Jeff Gothelf, 8 caixas (problema de negócio, resultados, usuários, benefícios, soluções, hipóteses, o que aprender primeiro, menor experimento).
- `pol-probe` (component) e `pol-probe-advisor` (interactive): escolhem o protótipo descartável mais barato entre 5 "flavors" (feasibility, task-focused, narrative, synthetic data, vibe-coded) para uma hipótese (`skills/pol-probe/SKILL.md` linhas 80-90).
- `problem-statement` e `problem-framing-canvas` (MITRE): enquadramento de problema.
- `tam-sam-som-calculator` (interactive, com script Python): dimensionamento de mercado com premissas explícitas.
- `customer-journey-map`, `opportunity-solution-tree`, `press-release` (Amazon working backwards).

## 4. Candidatos a Principle

São filosofias nomeadas que mudam o comportamento padrão do agente e valem fora de uma skill só:

1. **Fact / Inference / Assumption**: todo claim leva exatamente um rótulo, e o que não foi encontrado vai para uma lista de lacunas, não vira um quarto rótulo (`skills/autonomous-investigation/SKILL.md`, cláusula 3; reaparece em mais de 10 skills de investigação). É o candidato mais forte. Vale para BMC, VPC e personas, onde o risco é a hipótese virar fato.
2. **Research without a decision is a hobby**: nenhuma pesquisa sem a decisão que ela apoia (`autonomous-investigation` linha 35; `intelligence-collection-disciplines` linha 48: "If [DECISION] is blank, stop").
3. **Use the cheapest prototype that tells the harshest truth**: a "Golden Rule" do PoL probe, que parte do princípio de Jeff Patton "The most expensive way to test your idea is to build production-quality software" (`skills/pol-probe/SKILL.md` linhas 43 e 90). Seria o Principle natural se Wireframes for trocado.
4. **Proto, não validado** (mais fraco): documentos de cliente são hipóteses até a pesquisa validar (`proto-persona` linhas 22-50). Pode ser absorvido pelo item 1.
5. **ABC — Always Be Coaching** (`AGENTS.md`): é filosofia nomeada, mas de escrita de skills. Conflita com a ADR-0010 e não serve como Principle de execução. **[inferência]**

Nenhum desses vem como `SKILL.md` independente no formato Principle, porque estão embutidos em skills. Pela ADR-0004 (referência copiada byte a byte), não há texto para vendorar como Principle Community. Seriam Custom Principles (como `know-when-to-stop`, ADR-0009), escritos com nossas palavras, citando a origem como inspiração. **[inferência]**

## 5. Skills fora do escopo v1 que justificariam trocar um documento

- **Wireframes → PoL probe ou storyboard.** O repositório trata validação visual como escolha do protótipo mais barato para uma hipótese, não como wireframe. Um documento "probe" (hipótese, tipo de protótipo, critério de falha, plano de descarte) é mais útil para quem decide do que wireframes, que pedem ferramenta visual. Se ficar wireframe, nada daqui serve de base. **[inferência]**
- **BMC → Lean UX Canvas** se o plugin `product` precisar de um canvas de produto. BMC continua sem base aqui e cai no plugin `business`. **[inferência]**
- **Visão/Estratégia → positioning statement + press release.** Os dois são formatos curtos e testáveis. Um documento de visão poderia ser "positioning + PR/FAQ". **[inferência]**
- **ICP → TAM/SAM/SOM** como complemento de `business`: é a única skill quantitativa com script e premissas explícitas.
- **JTBD e VPC → fundir.** O JTBD daqui já é o perfil do cliente do VPC. Ter os dois documentos duplicaria jobs/pains/gains. **[inferência]**

## Lacunas

- Não li `examples/` linha a linha. A qualidade foi julgada pelo `SKILL.md`, pelo `template.md` e pelos tamanhos.
- Não li `commands/` (orquestrações que encadeiam skills) nem o repositório irmão `product-manager-prompts`.
- A leitura jurídica do NC/SA para um Marketplace MIT de uso pessoal/interno é minha interpretação, não um parecer. O próprio README sugere abrir issue em caso de dúvida.
