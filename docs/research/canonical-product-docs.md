# Fundamentos canônicos dos documentos de negócio e produto

Pesquisa para a issue Linear AI-60, filha do mapa AI-57 ("Plugins business e product v1"). Contexto: ADR-0012 (Document types e `references/<type>.md`). Escopo de partida do mapa: Business Model Canvas (BMC), Value Proposition Canvas (VPC), Visão e Estratégia de Produto, Personas / ICP, JTBD e Wireframes. Leitor principal dos documentos: humanos que decidem o negócio e o produto.

Pergunta: segundo as fontes primárias, qual é a estrutura canônica de cada documento, que decisão humana ele serve, como se sobrepõe aos outros e quais anti-padrões o tornam inútil?

Pesquisado em 2026-10-10. Cada afirmação cita a fonte. **[secundária]** marca afirmação sustentada só por fonte de terceiros. **[recomendação]** marca inferência minha, sem fonte que a decida; é insumo para grilling, não decisão.

## TL;DR

| Documento | Estrutura canônica (uma linha) | Decisão humana que serve |
|---|---|---|
| BMC | 9 blocos: Segmentos de clientes, Proposta de valor, Canais, Relacionamento, Receitas, Recursos, Atividades, Parcerias, Custos | O modelo de negócio inteiro é coerente e qual hipótese testar; comparar modelos alternativos |
| Lean Canvas | BMC com 4 blocos trocados: Problema, Solução, Métricas-chave, Vantagem injusta (+ Alternativas existentes, Early adopters, UVP de uma frase) | Qual par cliente-problema atacar e qual é a suposição mais arriscada agora (pré product-market fit) |
| VPC | Perfil do cliente (jobs, dores, ganhos) × Mapa de valor (produtos e serviços, aliviadores de dor, criadores de ganho), um por segmento × proposta | Quais dores e ganhos a oferta vai atacar (e quais não), e se há fit |
| JTBD | Job statement sem solução (verbo + objeto + contexto), executor, circunstância, dimensões funcional/social/emocional, job map, desired outcomes, forças de progresso | Que progresso o cliente quer fazer e contra o que competimos de fato; onde há necessidade mal atendida |
| Persona | Arquétipo fictício baseado em pesquisa: objetivos, comportamentos, atitudes, contexto; referencia os JTBD que se aplicam | Para quem desenhamos e como priorizar entre usuários com interesses conflitantes |
| ICP | Perfil da conta de melhor fit: características (firmográficas e outras) que fazem o cliente valorizar muito o valor diferenciado, mais desqualificadores | Em quais clientes/contas focar venda e marketing (go-to-market) |
| Visão e Estratégia | Visão: o futuro que queremos criar em 2 a 5 anos, como narrativa. Estratégia: kernel de Rumelt (diagnóstico, política-guia, ações coerentes) = foco, insights, ação | Para onde vamos e quais poucos problemas resolver agora, e portanto o que não fazer |
| Wireframe | Layout, conteúdo e design em nível de página, em baixa fidelidade; wireflow quando a tela muda com a interação | Qual alternativa de layout/fluxo seguir antes de investir em alta fidelidade ou código |

Recomendações de fundir/cortar **[recomendação]**:

1. **BMC + Lean Canvas → um Document type** (`business-model`), com a variante escolhida pelo estágio: Lean Canvas antes do product-market fit, BMC para negócio estabelecido. Cinco blocos são idênticos e Maurya diz que o Lean Canvas é uma adaptação do BMC para o empreendedor.
2. **VPC fica**, mas o Perfil do cliente cita os documentos de JTBD e persona em vez de reescrevê-los. Atenção: o nome "Customer Profile" do VPC colide com "perfil de cliente" (ICP) no glossário.
3. **JTBD fica como tipo próprio** (`jtbd`, já citado como exemplo no ADR-0012): é o documento mais estável (sem solução) e é a fonte que VPC e persona citam.
4. **Persona + ICP → um Document type** com duas seções (conta e pessoa) ou dois tipos em plugins diferentes (ICP em `business`, persona em `product`). Servem decisões diferentes (go-to-market vs. design), mas ambos descrevem "quem é o cliente" e confundi-los é o anti-padrão mais citado.
5. **Visão e Estratégia → um Document type** com duas seções de cadência diferente (visão estável por anos, estratégia revista com frequência). Roadmap fica fora do v1; os "themes" de Lombardo são as ações coerentes da estratégia.
6. **Wireframes → cortar como Document type.** É artefato visual descartável, não texto para o docs backend; já existe `foundation:prototype` para explorar UI. Se o `product` quiser algo, é uma skill que produz wireflows, não um tipo de documento.

## 1. Business Model Canvas (Strategyzer/Osterwalder)

**Estrutura.** Nove blocos que descrevem "who you serve, what you offer, how you deliver it, what it costs, and what it earns". Lado direito (mercado): segmentos de clientes, proposta de valor, canais, relacionamento com clientes, fontes de receita. Lado esquerdo (operação): atividades-chave, recursos-chave, parcerias-chave, estrutura de custos. A proposta de valor fica entre os dois lados. ([strategyzer.com/library/the-business-model-canvas](https://www.strategyzer.com/library/the-business-model-canvas)) A lista nominal dos nove blocos é a do livro *Business Model Generation* (Osterwalder e Pigneur, 2010); a página da Strategyzer só agrupa.

**Decisão que serve.** "Describe a business model on one page" e ver as interdependências: "Move a customer segment and the channels, activities, and costs all have to move with it." As células são suposições testáveis: "Date and version the canvas, then redraw it as evidence comes in." ([strategyzer.com](https://www.strategyzer.com/library/the-business-model-canvas))

**Anti-padrões.**
- "A filled-in canvas isn't a decision." O canvas preenchido não é o fim. ([strategyzer.com](https://www.strategyzer.com/library/the-business-model-canvas))
- Elementos órfãos: toda receita precisa de um segmento e de uma proposta que explique quem paga por quê ("advertising" sem "advertiser"). **[secundária]**: citação do Instruction Manual da Strategyzer via resultado de busca; o PDF não foi lido diretamente.
- Misturar presente e futuro no mesmo canvas; vários modelos num canvas só; detalhe demais que esconde o quadro geral. **[secundária]**, mesma origem. Os dois primeiros aparecem textualmente no manual do VPC (seção 3), que foi lido.

## 2. Lean Canvas (Ash Maurya)

**Estrutura.** Adaptação do BMC que troca quatro blocos:
- Entram **Problema** (top 1 a 3), **Solução** (box pequeno de propósito, para não "fall in love with your first solution"), **Métricas-chave** ("Failure to identify the right key metric can be catastrophic") e **Vantagem injusta** ("something that cannot be easily copied or bought").
- Saem **Atividades-chave e Recursos-chave** ("outside-in" focused), **Relacionamento com clientes** (absorvido por Canais) e **Parcerias-chave** ("most products do not fall into this category").
- Ficam Segmentos de clientes, Proposta de valor (como UVP), Canais, Receitas e Custos.
([ashmaurya.com/blog/why-lean-canvas-versus-business-model-canvas](https://ashmaurya.com/blog/why-lean-canvas-versus-business-model-canvas))
- Versões recentes do template acrescentam **Alternativas existentes** ao Problema e **Early adopters** ao Segmento, e a UVP é "a single, clear, compelling message". **[secundária]**: templates de terceiros, não confirmado em página da LEANSTACK.

**Para quem.** "Lean Canvas was designed for entrepreneurs, not consultants, customers, advisors, or investors." ([ashmaurya.com](https://ashmaurya.com/blog/why-lean-canvas-versus-business-model-canvas))

**Decisão que serve.** Qual par cliente-problema atacar e qual risco testar primeiro. Não há ordem certa de preenchimento: comece pelo backstory da ideia, estude a sua "chain of beliefs" e reordene por risco (cliente, mercado, técnico). ([ashmaurya.com/blog/what-is-the-right-fill-order-for-a-lean-canvas](https://ashmaurya.com/blog/what-is-the-right-fill-order-for-a-lean-canvas)) O par Problema-Cliente puxa o resto do canvas e segmentos amplos devem ser quebrados. ([blog.leanstack.com, via busca](https://blog.leanstack.com/what-is-the-right-fill-order-for-a-lean-canvas/))

**Anti-padrões.**
- Innovator's bias: "fake" os boxes de cliente e problema para justificar a solução que já se quer construir. ([ashmaurya.com](https://ashmaurya.com/blog/what-is-the-right-fill-order-for-a-lean-canvas))
- Solução grande demais, que vira legado antes de validar o problema. ([ashmaurya.com](https://ashmaurya.com/blog/why-lean-canvas-versus-business-model-canvas))
- Métrica-chave errada, que leva a otimização prematura. (idem)

## 3. Value Proposition Canvas (Strategyzer)

**Estrutura.** "A plug-in tool to the Business Model Canvas" que detalha os blocos Proposta de valor e Segmento de clientes e avalia o "fit" entre eles. ([Instruction Manual, PDF](https://assets.strategyzer.com/assets/resources/the-value-proposition-canvas-instruction-manual.pdf))
- **Perfil do cliente:** Customer Jobs ("every major and ancillary job"), Pains ("before, during, and after getting the job done"), Gains ("every benefit your customer expects, desires or would be surprised by"). (manual)
- **Mapa de valor:** Products & Services, Pain Relievers, Gain Creators. (manual)
- Jobs são funcionais, sociais ou emocionais; dores e ganhos são ranqueados por intensidade e frequência. ([strategyzer.com](https://www.strategyzer.com/library/achieve-product-market-fit-with-our-brand-new-value-proposition-designer-canvas))
- Três fits: problem-solution, product-market e business model fit. ([strategyzer.com, via busca](https://www.strategyzer.com/value-proposition))
- Ordem do manual: jobs, depois dores e ganhos, depois produtos e serviços, depois aliviadores e criadores.

**Decisão que serve.** Quais dores e ganhos a oferta ataca e se o fit se sustenta. Usado antes da pesquisa, mostra o que aprender; depois, avalia o fit. (manual)

**Anti-padrões** (seção "Frequently Committed Mistakes" do manual, lido diretamente):
- Tentar aliviar toda dor e criar todo ganho: "Great value propositions often focus on a limited number of pain relievers and gain creators."
- Misturar presente e futuro.
- Vários segmentos ou propostas num mapa: "Focus on one value proposition for a specific customer segment on a single map."
- Paralisia de análise: "A great Value Proposition with a great 'fit' on paper is just an untested fantasy."

## 4. Jobs to be Done (Christensen, Ulwick, Moesta)

As três escolas concordam no núcleo e divergem na forma.

**Christensen.** Um job é "the progress that a person is trying to make in a particular circumstance" (*Competing Against Luck*, 2016; definição reproduzida em várias fontes **[secundária]**, o artigo da HBR não carregou). O Christensen Institute: "People don't simply buy or pick products or services; they pull them into their lives to make progress", a circunstância muda o job, e todo job tem dimensões funcional, social e emocional. Alerta contra segmentar por demografia ou atributos de produto. ([christenseninstitute.org/theory/jobs-to-be-done](https://www.christenseninstitute.org/theory/jobs-to-be-done/))

**Ulwick (Outcome-Driven Innovation).** ([strategyn.com/jobs-to-be-done](https://strategyn.com/jobs-to-be-done/))
- Core functional job "in a single, solution-free statement" ("cut a piece of wood in a straight line"). Formato verbo + objeto + esclarecedor de contexto ([JTBD Canvas, strategyn.com](https://strategyn.com/wp-content/uploads/2024/06/JTBD-Canvas.pdf), via busca).
- Job map universal em 8 passos: Define, Locate, Prepare, Confirm, Execute, Monitor, Modify, Conclude.
- 50 a 150 desired outcomes por mercado, medidos por importância e satisfação. Formato: direção (minimize/increase) + métrica + objeto de controle + contexto, por exemplo "Minimize the time it takes to locate a file during a patient consultation". **[secundária]** para o formato.
- Papéis: job executor, comprador, equipe de suporte do ciclo de vida.

**Moesta e Spiek (forças de progresso).** "Push + Pull > Anxiety + Habit → the switch happens." Push é o problema da situação atual, Pull o magnetismo do novo, Anxiety o medo do desconhecido, Habit a inércia. As forças aparecem em switch interviews e na linha do tempo da decisão. ([jobstobedone.org/the-four-forces](https://jobstobedone.org/the-four-forces/))

**Decisão que serve.** Contra o que competimos de fato (inclusive não consumo e gambiarras) e onde há necessidade mal atendida para priorizar. Ulwick liga os outcomes à escolha de estratégia de crescimento (diferenciada, dominante, disruptiva...). (strategyn.com)

**Anti-padrões.**
- Job com solução ou adjetivo dentro ("usar um app para..."): deixa de ser estável. (strategyn.com)
- Segmentar por atributos do cliente em vez de circunstância. (christenseninstitute.org)
- Só forças de atração: ignorar Anxiety e Habit, que explicam por que um produto melhor perde. **[secundária]** (resumos do modelo de Moesta)

## 5. Persona, ICP e a relação com JTBD

**Persona.** Cooper introduziu personas como "hypothetical archetypes of actual users" no Goal-Directed Design (*The Inmates Are Running the Asylum*, 1998). **[secundária]** (resumos do livro) A NN/g define persona como "a fictional, yet realistic, description of a typical or target user" usada para empatia, priorização de features e decisões de design ([nngroup.com/articles/persona](https://www.nngroup.com/articles/persona/), via busca). Conteúdo: detalhes demográficos, mas sobretudo atitudes, cognição e comportamento. ([nngroup.com/articles/personas-jobs-be-done](https://www.nngroup.com/articles/personas-jobs-be-done/))

**Persona × JTBD (NN/g).** Não competem: "users and tasks: we need both". JTBD é uma frase sobre o que o usuário precisa realizar e generaliza para toda a base; persona acrescenta contexto e empatia e ajuda a "balance design considerations among many different kinds of users, who often have competing interests" (o empreiteiro e o dono da casa têm o mesmo job de furar a parede, mas valorizam atributos diferentes). Integração recomendada: "each persona artifact reference the already existing jobs-to-be-done that apply to that particular persona". ([nngroup.com](https://www.nngroup.com/articles/personas-jobs-be-done/))

**Anti-padrões de persona (NN/g).** Criada e não usada; sem apoio da liderança; feita em silo e imposta; falta de entendimento do que é; escopo sem objetivo definido ("not a one-size-fits-all tool"); polida demais para ser atualizada e por isso desatualizada. ([nngroup.com/articles/why-personas-fail](https://www.nngroup.com/articles/why-personas-fail/)) Proto-personas, feitas sem pesquisa nova, alinham suposições do time mas "should be used with caution". ([nngroup.com/articles/persona-types](https://www.nngroup.com/articles/persona-types/), via busca) Persona puramente demográfica é o mal-entendido que leva a querer trocá-la por JTBD. (personas-jobs-be-done)

**ICP.** Não tem autor canônico; a fonte mais próxima de primária é April Dunford: best-fit customers são os que "care a lot about your differentiated value", entendem o valor fácil, compram mais rápido e pedem menos desconto; caracterizá-los começa por indústria, local e porte, mas precisa ficar "super specific". ([aprildunford.com/post/a-quickstart-guide-to-positioning](https://www.aprildunford.com/post/a-quickstart-guide-to-positioning), via busca) A literatura de vendas B2B separa ICP (a conta: firmografia, tecnografia, sinais de fit) de buyer persona (a pessoa no comitê de compra). **[secundária]** (ZoomInfo, Gartner Digital Markets e outros, via busca)

**Sobreposição.** ICP responde "quais contas" (go-to-market, lado `business`); persona responde "para quem desenhamos" (lado `product`); JTBD responde "que progresso", independente de quem. Os três alimentam o Perfil do cliente do VPC e o bloco Segmentos de clientes do BMC/Lean Canvas.

## 6. Visão e Estratégia de Produto (Cagan, Rumelt, Lombardo)

**Visão (Cagan).** Descreve "the future we are trying to create, typically somewhere between 2 and 5 years out"; forma livre: storyboard, narrativa ou "visiontype" (protótipo em vídeo); propósito: inspirar times, investidores e parceiros. "Stubborn on the vision, and flexible on the details." ([svpg.com/vision-vs-strategy](https://www.svpg.com/vision-vs-strategy/)) Mantém o foco no cliente e é a "North Star" comum. ([svpg.com/product-vision-vs-mission](https://www.svpg.com/product-vision-vs-mission/))

**Estratégia (Cagan).** "How do we make the product vision a reality, while meeting the needs of the company as we go?" Quatro partes: foco (escolher poucas coisas, "and therefore all the things you won't do"), insights, ação (transformar insights em objetivos para os times) e gestão. Visão é o destino, estratégia o caminho, roadmap é tática. ([svpg.com/product-strategy-overview](https://www.svpg.com/product-strategy-overview/))

**Kernel (Rumelt, *Good Strategy/Bad Strategy*, 2011).** Diagnóstico (a natureza do desafio), política-guia (a abordagem que restringe a ação) e ações coerentes. Sinais de estratégia ruim: fluff, não encarar o desafio, confundir metas com estratégia e objetivos estratégicos ruins. **[secundária]** (resumos do livro; o artigo do autor na McKinsey Quarterly, "The perils of bad strategy", não carregou). Cagan cita Rumelt: "bad strategy is the active avoidance of the hard work of crafting a good strategy". (svpg.com/product-strategy-overview)

**Roadmap (Lombardo et al., *Product Roadmaps Relaunched*, 2017).** Componentes primários: visão do produto, objetivos de negócio, themes ("what would need to be true for our product to realise its vision"), timeframes amplos e disclaimer; secundários: features, estágio, confiança, clientes-alvo, áreas. Roadmap é ferramenta de comunicação estratégica, não plano de projeto. **[secundária]** (O'Reilly bloqueou; notas de leitores e resumos)

**Decisão que serve.** Para onde vamos, quais poucos problemas atacar agora e o que fica de fora.

**Anti-padrões.**
- Visão como slogan de missão. (svpg.com/product-vision-vs-mission)
- Uma visão por time, "everyone picking out their own star from the sky". (idem)
- Metas de negócio e roadmap de features sem estratégia ligando os dois. (svpg.com/vision-vs-strategy)
- Querer entregar a visão inteira numa release, "the antithesis of the concept of minimum viable product". (idem)
- Fluff, desafio não diagnosticado, meta disfarçada de estratégia, lista de 50 objetivos. (Rumelt **[secundária]**; svpg.com/product-strategy-overview)

## 7. Wireframes

**Estrutura.** Wireframe comunica "page-level layout ideas, content, and page-level design"; wireflow combina layouts de wireframe com um fluxograma simplificado das interações e serve melhor apps em que conteúdo e layout mudam com a interação. ([nngroup.com/articles/wireflows](https://www.nngroup.com/articles/wireflows/)) Baixa fidelidade deixa explorar várias alternativas e mudar o desenho entre sessões de teste. ([nngroup.com/articles/ux-prototype-hi-lo-fidelity](https://www.nngroup.com/articles/ux-prototype-hi-lo-fidelity/), via busca)

**Decisão que serve.** Qual alternativa de layout e fluxo seguir antes de gastar com alta fidelidade ou código.

**Anti-padrões.**
- Wireframes estáticos para telas dinâmicas: perdem a interação. Fluxograma sem tela perde o contexto. (nngroup.com/articles/wireflows)
- Uma alternativa só, ou fidelidade alta cedo, o que mata a exploração que justifica o artefato. (ux-prototype-hi-lo-fidelity)

**Encaixe no Marketplace** **[recomendação]**: o wireframe é descartável e visual, não um registro de decisão para o docs backend (ADR-0005), e `foundation:prototype` já explora UI com protótipos descartáveis. Por isso não deveria ser Document type.

## 8. Mapa de sobreposições

- **BMC ↔ Lean Canvas:** cinco blocos iguais (Segmentos, Proposta/UVP, Canais, Receitas, Custos). O Lean troca os quatro blocos operacionais por blocos de risco. A escolha é por estágio e leitor: o empreendedor antes do fit (Lean) ou alguém descrevendo um negócio existente (BMC). (ashmaurya.com)
- **BMC ↔ VPC:** o VPC é um zoom em dois blocos do BMC. (manual do VPC)
- **VPC ↔ JTBD:** Customer Jobs do VPC é JTBD em forma rasa (lista de jobs). JTBD completo traz circunstância, job map, outcomes mensuráveis e forças, que o VPC não tem. Dores e ganhos do VPC são parecidos com os desired outcomes de Ulwick **[recomendação]**.
- **VPC ↔ Persona/ICP:** o Perfil do cliente descreve um segmento; persona e ICP dão o "quem" que nomeia esse segmento.
- **Persona ↔ JTBD:** complementares; a persona referencia os JTBD (NN/g).
- **Persona ↔ ICP:** pessoa vs. conta; em B2C quase colapsam, em B2B divergem **[secundária]**.
- **Visão/Estratégia ↔ BMC:** a estratégia precisa ser viável no modelo de negócio ("meeting the needs of the company as we go", Cagan). O BMC é o teste de viabilidade da estratégia **[recomendação]**.
- **Ordem natural de produção** **[recomendação]**: JTBD e Persona/ICP → VPC → modelo de negócio (Lean ou BMC) → Visão e Estratégia, com a estratégia podendo vir antes como hipótese.

## 9. Insumo para `references/<type>.md`

Cada reference deveria trazer, a partir das fontes acima:

1. a decisão humana que o documento serve (linha da tabela do TL;DR), para o leitor saber quando ele está pronto;
2. a estrutura canônica com a pergunta de cada seção;
3. a regra de unidade: um canvas por segmento × proposta (VPC), um modelo por canvas (BMC), um job central por documento JTBD, uma visão por organização de produto;
4. a separação presente/futuro (status "atual" vs. "hipótese"), comum a BMC e VPC;
5. os anti-padrões da seção do tipo, como checklist de revisão;
6. as citações a outros documentos em vez de cópia (VPC cita JTBD e persona; persona cita JTBD; estratégia cita o modelo de negócio);
7. versão e data, porque as fontes tratam todo canvas como hipótese a redesenhar com evidência.

## Fontes não acessadas

- HBR, "Know Your Customers' Jobs to Be Done" (Christensen et al., 2016): paywall.
- McKinsey Quarterly, "The perils of bad strategy" (Rumelt, 2011): timeout.
- O'Reilly, *Product Roadmaps Relaunched*, cap. 2: 403.
- Business Model Canvas Instruction Manual (PDF): não lido; mistakes citados via busca.
- Páginas oficiais do Lean Canvas na LEANSTACK: 404 e redirecionamentos para ashmaurya.com (usado).
