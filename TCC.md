# HubAgents V2: Sistema Multi-Agente para Análise de Risco de Violência Doméstica utilizando Large Language Models

## Autor
Cairo Gabriel Castadini Cruz

## Orientador
Prof. Dr. Paulo Henrique Ribeiro Gabriel

## Instituição
Universidade Federal de Uberlândia – UFU
Faculdade de Computação
Bacharelado em Sistemas de Informação

## Ano
2025

## Resumo
A violência doméstica configura-se como um grave problema de saúde pública que exige ferramentas tecnológicas inovadoras para detecção precoce e prevenção. Este trabalho apresenta o desenvolvimento do **HubAgents V2**, um sistema multi-agente baseado em Large Language Models (LLMs) para a análise automatizada de risco em contextos de violência doméstica. O sistema implementa uma arquitetura composta por cinco agentes especializados que analisam diferentes dimensões contextuais através de técnicas de Processamento de Linguagem Natural (PLN) e *few-shot learning*. Utilizando o **Microsoft Agent Framework** (ou **AutoGen**) e o framework **FastAPI** para exposição via API REST, o sistema opera em um pipeline de três fases: análise paralela por agentes especialistas, controle de qualidade via agente supervisor e síntese consolidada com um *score* quantitativo. A API REST desenvolvida possibilita a integração com plataformas de atendimento e sistemas de triagem, funcionando como uma primeira linha de avaliação automatizada. A validação através de casos de teste demonstrou a capacidade do sistema de identificar padrões complexos de risco com justificativas fundamentadas, oferecendo uma alternativa escalável e consistente aos protocolos manuais tradicionais. Os resultados indicam que a abordagem multi-agente proporciona especialização por domínio, transparência nas avaliações e uma arquitetura extensível para a incorporação de novos critérios analíticos.

## Palavras-chave
sistemas multi-agente, large language models, análise de risco, violência doméstica, inteligência artificial, API REST, Microsoft Agent Framework, processamento de linguagem natural.

---

## Estrutura do Documento

### 1 INTRODUÇÃO

#### 1.1 Motivação: IA como Ferramenta de Prevenção e Primeiro Atendimento
A violência doméstica é um fenômeno complexo e multifacetado que afeta milhões de pessoas globalmente. A detecção precoce de sinais de risco pode ser determinante para evitar a escalada da violência. No entanto, os canais de atendimento tradicionais muitas vezes enfrentam sobrecarga e limitações de disponibilidade. A Inteligência Artificial (IA), especificamente os Grandes Modelos de Linguagem (LLMs), oferece uma oportunidade única para criar ferramentas de triagem acessíveis, escaláveis e capazes de analisar nuances textuais em relatos de vítimas.

O HubAgents V2 surge como uma resposta tecnológica a essa demanda, propondo um sistema que não substitui o julgamento humano, mas atua como uma camada preliminar de análise, capaz de identificar padrões de risco em relatos textuais e fornecer *insights* estruturados para profissionais de assistência social e segurança pública.

#### 1.1.1 Fundamentação Teórica da Aplicação
A aplicação baseia-se na teoria de Sistemas Multi-Agente (MAS), onde entidades autônomas colaboram para resolver problemas complexos. Ao dividir a análise de risco em domínios específicos (emocional, financeiro, físico, etc.), o sistema emula uma junta multidisciplinar de especialistas, reduzindo o viés de uma única análise e aumentando a precisão através da especialização.

#### 1.2 Objetivos

##### 1.2.1 Objetivo Geral
Desenvolver e validar um sistema multi-agente baseado em LLMs para a análise automatizada e classificada de risco em relatos de violência doméstica, disponibilizado através de uma API REST.

##### 1.2.2 Objetivos Específicos
- Implementar uma arquitetura de agentes especialistas focados em diferentes dimensões da violência doméstica (psicológica, física, patrimonial, etc.).
- Desenvolver um mecanismo de supervisão automática para garantir a qualidade e consistência das análises geradas pelos agentes.
- Criar um agente sintetizador capaz de consolidar múltiplos relatórios em um *score* de risco unificado.
- Expor o sistema através de uma API REST de alta performance utilizando FastAPI.
- Validar a eficácia do sistema através de cenários de teste controlados.

#### 1.3 API REST como Solução de Classificação
A escolha por uma arquitetura de API REST permite que o HubAgents V2 seja agnóstico à plataforma de interface. Isso significa que o "cérebro" de análise de risco pode ser integrado a *chatbots* no WhatsApp, portais web, aplicativos móveis ou sistemas internos de delegacias e centros de apoio, facilitando sua adoção em diferentes pontos de contato com a vítima.

#### 1.4 Justificativa
A automação da análise de risco inicial permite uma resposta imediata e consistente, independente do horário ou da carga de trabalho dos atendentes humanos. Além disso, a abordagem estruturada e explicável dos agentes fornece uma base documental que pode auxiliar na priorização de casos urgentes.

#### 1.5 Organização do Trabalho
O trabalho está organizado em cinco capítulos. O Capítulo 2 apresenta a fundamentação teórica sobre agentes, LLMs e as tecnologias empregadas. O Capítulo 3 detalha o desenvolvimento do sistema, sua arquitetura e implementação. O Capítulo 4 apresenta os resultados obtidos através de um estudo de caso. Por fim, o Capítulo 5 traz as conclusões e sugestões para trabalhos futuros.

---

### 2 FUNDAMENTAÇÃO TEÓRICA

#### 2.1 Agentes de Inteligência Artificial

##### 2.1.1 Conceitos Fundamentais
Um agente de IA pode ser definido como um sistema computacional situado em um ambiente, capaz de agir de forma autônoma para alcançar objetivos delegados. Agentes modernos não apenas reagem a entradas, mas planejam, raciocinam e interagem.

##### 2.1.2 Sistemas Multi-Agente (MAS)
Sistemas Multi-Agente consistem em múltiplos agentes interagindo. A vantagem principal é a decomposição de problemas: em vez de um modelo monolítico tentar resolver tudo, especialistas focam em subproblemas. No contexto deste trabalho, isso se traduz em agentes que "olham" para o problema sob lentes diferentes (financeira, psicológica, etc.).

##### 2.1.3 Agentes Baseados em LLM
A emergência dos LLMs permitiu a criação de agentes cognitivos que utilizam o modelo de linguagem como núcleo de raciocínio (*reasoning engine*). Estes agentes podem interpretar instruções complexas em linguagem natural, manter contexto e gerar saídas estruturadas.

#### 2.2 Large Language Models (LLMs)

##### 2.2.1 Arquitetura Transformer e Capacidades Emergentes
Os LLMs, baseados na arquitetura Transformer, revolucionaram o processamento de linguagem natural. Sua capacidade de atenção (*self-attention*) permite capturar dependências de longo prazo em textos, essencial para entender narrativas complexas de violência doméstica onde o contexto é crucial.

##### 2.2.2 Few-Shot Learning e Contextualização
A técnica de *Few-Shot Learning* (aprendizado com poucos exemplos) é utilizada neste projeto para "ensinar" aos agentes o padrão de análise desejado sem a necessidade de re-treinar o modelo. Ao fornecer exemplos de análises de risco no *prompt* do sistema, os agentes alinham suas respostas ao formato e profundidade esperados.

##### 2.2.3 Limitações e Considerações Éticas
É fundamental reconhecer que LLMs podem alucinar (gerar informações falsas) ou reproduzir vieses. Por isso, a arquitetura deste projeto inclui camadas de supervisão e revisão, e o sistema é posicionado como ferramenta de apoio à decisão, e não como decisor final autônomo.

#### 2.3 Ferramentas e Tecnologias Utilizadas

##### 2.3.1 Microsoft Agent Framework (ou AutoGen)
O projeto utiliza o Microsoft Agent Framework como orquestrador. Ele facilita a criação de agentes conversáveis, o gerenciamento de estado e a troca de mensagens entre especialistas, supervisor e sintetizador.

##### 2.3.2 FastAPI: Alto Desempenho para APIs de IA
FastAPI é um framework moderno para construção de APIs em Python. Sua escolha deve-se ao suporte nativo a processamento assíncrono (`async/await`), essencial para lidar com múltiplas chamadas de LLM simultaneamente sem bloquear o servidor, além da integração automática com documentação Swagger.

##### 2.3.3 Pydantic e Validação de Dados
Pydantic é utilizado para garantir que as saídas dos LLMs (que são probabilísticas) sigam esquemas rígidos de dados. Isso transforma texto não estruturado em objetos JSON confiáveis, com campos tipados para *scores*, listas de fatores e justificativas.

##### 2.3.4 Groq: Inferência Acelerada de LLM
Para viabilizar o uso em tempo real, o projeto utiliza a infraestrutura da Groq, que oferece inferência de modelos Llama 3 e Mixtral com latência extremamente baixa, permitindo que o sistema multi-agente complete seu ciclo de raciocínio complexo em segundos.

#### 2.4 Trabalhos Relacionados

##### 2.4.1 Sistemas Multi-Agente para Análise de Risco
A literatura recente explora MAS em finanças e logística, mas a aplicação em análise de risco social é um campo emergente. O HubAgents V2 contribui ao aplicar padrões de colaboração (especialista-revisor) neste domínio sensível.

##### 2.4.2 Machine Learning para Detecção de Violência Doméstica
Abordagens tradicionais de ML (como SVM ou Random Forest) dependem de *datasets* rotulados massivos. A abordagem com LLMs proposta aqui supera o problema da escassez de dados rotulados através da generalização semântica e do *few-shot prompting*.

---

### 3 DESENVOLVIMENTO DO SISTEMA MULTI-AGENTE

#### 3.1 Arquitetura Geral do Sistema

##### 3.1.1 Visão de Componentes e Fluxo de Dados
O sistema segue uma arquitetura de pipeline orquestrado. A requisição chega via API, é distribuída para análise, revisada e então sintetizada.

**Tabela de Componentes e Responsabilidades:**

| Componente | Tipo | Responsabilidade |
| :--- | :--- | :--- |
| **API Gateway** | FastAPI | Receber requisições HTTP, validar entrada e retornar resposta final. |
| **Orquestrador** | Controller | Gerenciar o fluxo de dados entre as fases e controlar concorrência. |
| **Agentes Especialistas (x5)** | LLM Agent | Analisar o relato sob uma ótica específica (ex: Psicológica, Patrimonial). |
| **Agente Supervisor** | LLM Agent | Revisar a qualidade das análises dos especialistas (Critique/Refine). |
| **Agente Sintetizador** | LLM Agent | Consolidar os 5 relatórios em um único score e parecer final. |

#### 3.2 Pipeline de Processamento em Três Fases

##### 3.2.1 Fase 1: Análise Paralela por Agentes Especializados
Nesta fase, o relato da usuária (composto por 5 respostas a perguntas chave) é enviado simultaneamente para 5 agentes distintos. Cada agente possui um *System Prompt* único que define sua "persona" e foco:
1.  **Agente 1:** Rotina e Divisão de Tarefas.
2.  **Agente 2:** Aspectos Emocionais e Comunicação.
3.  **Agente 3:** Redes de Apoio e Isolamento.
4.  **Agente 4:** Controle Financeiro/Patrimonial.
5.  **Agente 5:** Bem-estar Físico e Psicológico.

Isso garante que nenhum aspecto da violência seja negligenciado.

##### 3.2.2 Fase 2: Controle de Qualidade via Agente Supervisor
Diferente de sistemas simples de "pergunta-resposta", o HubAgents V2 implementa um loop de feedback. As análises da Fase 1 são submetidas a um Agente Supervisor. Este agente avalia a coerência, profundidade e a justificativa do *score* atribuído. Se a análise for considerada superficial ou contraditória, o Supervisor a rejeita com feedback específico, e o Especialista deve refazer a análise (limitado a 1 retrabalho para evitar loops infinitos).

##### 3.2.3 Fase 3: Síntese e Consolidação
Após a aprovação de todos os relatórios especializados, o Agente Sintetizador recebe o conjunto completo de dados. Sua função não é apenas somar médias, mas interpretar a correlação entre os fatores (ex: controle financeiro causando isolamento social) e gerar um *Risk Score* final (0-100), uma classificação de risco (Baixo/Médio/Alto) e recomendações práticas.

#### 3.3 Implementação dos Componentes

##### 3.3.1 Estrutura de Diretórios e Organização do Código
O projeto segue uma estrutura modular para facilitar a manutenção e escalabilidade.

**Tabela de Estrutura de Diretórios:**

| Diretório | Conteúdo |
| :--- | :--- |
| `/agents` | Lógica dos agentes (fábrica, especialistas, supervisor, sintetizador). |
| `/models` | Definições de esquemas de dados (Pydantic schemas). |
| `/prompts` | Templates de prompts de sistema e engenharia de prompt. |
| `/services` | Integração com provedores de LLM (OpenAI, Azure, Groq). |
| `/data` | Dados para *few-shot learning* (exemplos). |
| `main.py` | Ponto de entrada da aplicação FastAPI. |

##### 3.3.2 Modelos de Dados e Tipagem
Utilizando Pydantic, definimos estritamente o formato de entrada e saída.

Exemplo de Modelo de Saída do Especialista (`SpecialistReport`):
- `agent_id`: Identificador do agente.
- `domain`: Domínio de análise.
- `risk_factors`: Lista de objetos `RiskFactor` (fator, severidade, descrição).
- `preliminary_score`: Float (0-100).
- `justification`: Texto explicativo.

##### 3.3.3 Abstração Multi-Provider de LLM
O sistema foi desenhado para não depender de um único fornecedor de IA. Uma camada de abstração permite alternar entre Azure OpenAI, OpenAI padrão e Groq via variáveis de ambiente, garantindo flexibilidade de custos e performance.

##### 3.3.4 Sistema de Logging e Rastreabilidade
Todas as etapas do processo (recebimento, análises individuais, feedbacks do supervisor, síntese) são logadas com *timestamps*. Isso é crucial para auditoria e para entender o "raciocínio" do sistema em caso de falhas ou resultados inesperados.

#### 3.4 Decisões de Design

##### 3.4.1 Processamento Assíncrono e Escalabilidade
O uso de `async/await` em Python permite que, enquanto o sistema aguarda a resposta da LLM (IO-bound), o servidor possa aceitar novas requisições.

##### 3.4.2 Limite de Retrabalho
Para evitar custos infinitos e latência alta, o loop de revisão do supervisor tem um limite rígido (`MAX_REWORK = 1`). Se o especialista falhar duas vezes, a melhor resposta disponível é utilizada, mas o evento é logado como alerta.

##### 3.4.3 Thresholds de Classificação
Os níveis de risco foram calibrados empiricamente nos prompts:
- 0-30: Baixo
- 31-65: Médio
- 66-100: Alto

---

### 4 RESULTADOS E ANÁLISE DE CASO

#### 4.1 Contextualização do Caso de Teste
Para validar o sistema, foi submetido um caso de teste contendo respostas que indicam um cenário de violência psicológica e controle progressivo.

**Nota sobre os Dados:** É importante ressaltar que os dados utilizados neste estudo de caso, bem como o dataset de exemplos (*few-shot*) utilizados para calibrar os agentes, são **inteiramente sintéticos**. Eles foram gerados artificialmente para simular padrões reais de violência doméstica descritos na literatura, visando preservar a privacidade de vítimas reais e servir exclusivamente como prova de conceito tecnológica.

#### 4.2 Entrada do Sistema e Modelo de Dados
O sistema recebeu um JSON contendo 5 respostas simulando um relato de usuária.

**Tabela de Entrada do Sistema:**

| ID | Resposta da Usuária (Simulada) |
| :--- | :--- |
| 1 | "Sim, ele às vezes grita comigo quando está estressado com o trabalho." |
| 2 | "Não, nunca tivemos problemas sérios, mas ele fica bravo se eu demoro na rua." |
| 3 | "Ele controla muito o que eu faço e com quem eu falo." |
| 4 | "Não tenho família por perto, mudei de cidade por causa dele." |
| 5 | "Tenho medo às vezes de como ele vai reagir se eu discordar." |

#### 4.3 Walkthrough Detalhado do Processamento

##### 4.3.1 Fase 1: Análises Especializadas (Saída dos 5 Agentes)
Os agentes processaram as respostas em paralelo. Abaixo, um exemplo da saída do Agente Especialista em Controle e Isolamento (Agente 3).

**Exemplo de Saída JSON (Agente 3):**
```json
{
  "agent_id": "3",
  "domain": "Redes de Apoio e Isolamento",
  "analysis": "A usuária relata isolamento geográfico ('mudei de cidade') e controle sobre interações sociais ('com quem eu falo'). Isso configura um cenário clássico de isolamento social forçado.",
  "preliminary_score": 85.0,
  "risk_factors": [
    {
      "factor": "Isolamento Geográfico",
      "severity": "Alto",
      "description": "Mudança de cidade e ausência de família próxima."
    },
    {
      "factor": "Monitoramento Social",
      "severity": "Alto",
      "description": "Controle sobre com quem a vítima interage."
    }
  ],
  "justification": "O isolamento remove a rede de proteção da vítima, aumentando drasticamente a vulnerabilidade e dependência."
}
```

##### 4.3.2 Fase 2: Revisão de Qualidade pelo Agente Supervisor
O Supervisor analisou o relatório acima.

**Tabela de Revisão:**
| Agente | Status | Feedback |
| :--- | :--- | :--- |
| Agente 3 | APROVADO | "Análise consistente e bem fundamentada nos fatos apresentados." |
| Agente 1 | REVISAR | "A justificativa está muito genérica. Cite trechos específicos da resposta 1." |

*Nota: O Agente 1 refez sua análise conforme instruído antes de prosseguir.*

##### 4.3.3 Fase 3: Síntese Consolidada e Score Final
O Agente Sintetizador agregou as visões parciais (Emocional, Controle, Isolamento) em um laudo final.

**Tabela de Saída Final - FinalAnalysis:**
| Campo | Valor |
| :--- | :--- |
| **Score Final** | **78.5** |
| **Risco** | **ALTO** |
| **Síntese** | A análise integrada revela um padrão sistemático de controle coercitivo. O isolamento geográfico (Agente 3) potencializa o medo relatado (Agente 2) e o controle comportamental (Agente 4). Há indicadores claros de violência psicológica que podem escalar. |
| **Recomendações** | 1. Buscar contato discreto com rede de apoio online. <br> 2. Documentar episódios de controle. <br> 3. Não confrontar diretamente em momentos de estresse do agressor. |

#### 4.5 Interpretação e Discussão dos Resultados

##### 4.5.1 Qualidade da Análise e Transparência
O sistema demonstrou capacidade de "explicar" seu raciocínio. Ao invés de apenas dar um número (ex: "Risco 78%"), ele detalha *por que* chegou a esse número (isolamento + controle + medo), o que é vital para a confiança do usuário (XAI - Explainable AI).

##### 4.5.2 Limitações Observadas no Caso
Em casos onde a ambiguidade é alta (ex: sarcasmo ou negação implícita), os modelos podem divergir. O mecanismo de supervisão mitigou isso, mas não elimina totalmente a necessidade de revisão humana em casos limítrofes.

##### 4.5.3 Comparação com Protocolos Tradicionais
Comparado a um formulário estático (checklist), o sistema foi capaz de inferir riscos a partir de nuances de linguagem ("medo de como ele vai reagir") que poderiam passar despercebidas em respostas de múltipla escolha.

---

### 5 CONCLUSÃO

#### 5.1 Síntese do Trabalho Realizado
O HubAgents V2 atingiu seu objetivo de implementar um sistema robusto de análise de risco. A arquitetura de múltiplos especialistas provou-se eficaz para cobrir as diversas facetas da violência doméstica, enquanto o uso de LLMs modernos garantiu fluidez e profundidade interpretativa.

#### 5.2 Contribuições Científicas e Técnicas
- **Arquitetura Replicável:** O padrão de design (Especialistas -> Supervisor -> Sintetizador) pode ser aplicado a outros domínios de diagnóstico.
- **Validação de Frameworks:** Demonstração prática do uso do Microsoft Agent Framework em conjunto com FastAPI em um contexto crítico.
- **Engenharia de Prompt:** Desenvolvimento de *prompts* estruturados que garantem saídas determinísticas (JSON) a partir de modelos probabilísticos.

#### 5.3 Limitações Identificadas
A dependência de conexão com a internet para acesso às APIs de LLM e o custo por token são barreiras para implementação em locais com recursos escassos. Além disso, o uso de dados sintéticos limita a validação definitiva da acurácia clínica do sistema.

#### 5.4 Trabalhos Futuros
- Realizar validação com dados reais anonimizados em parceria com instituições de apoio.
- Implementar modelos locais (SLMs - Small Language Models) para rodar *offline* em dispositivos móveis.
- Adicionar um agente de "Triagem de Emergência" que detecte risco iminente de vida e acione protocolos de alerta imediato, furando a fila de processamento padrão.

#### 5.5 Considerações Finais
A tecnologia não é a solução final para a violência doméstica, mas é uma aliada poderosa. O HubAgents V2 representa um passo em direção a um atendimento mais ágil, empático e inteligente, colocando a IA a serviço da proteção humana.

---

## REFERÊNCIAS

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. **NBR 14724**: informação e documentação: trabalhos acadêmicos: apresentação. Rio de Janeiro, 2011.

BROWN, Tom B. et al. Language models are few-shot learners. **NeurIPS**, v. 33, p. 1877-1901, 2020.

FASTAPI. **FastAPI Framework**. Disponível em: <https://fastapi.tiangolo.com/>. Acesso em: 15 mai. 2025.

MICROSOFT. **AutoGen: Enabling Next-Gen LLM Applications**. Disponível em: <https://microsoft.github.io/autogen/>. Acesso em: 10 jun. 2025.

OPENAI. **GPT-4 Technical Report**. arXiv preprint arXiv:2303.08774, 2023.

RUSSELL, Stuart; NORVIG, Peter. **Artificial Intelligence: A Modern Approach**. 4. ed. Pearson, 2020.

VASWANI, Ashish et al. Attention is all you need. **Advances in neural information processing systems**, v. 30, 2017.

WHO. **Violence against women**. World Health Organization, 2021. Disponível em: <https://www.who.int/news-room/fact-sheets/detail/violence-against-women>. Acesso em: 20 jan. 2025.

WOOLDRIDGE, Michael. **An Introduction to MultiAgent Systems**. 2. ed. John Wiley & Sons, 2009.

---

## APÊNDICES

### APÊNDICE A - Exemplo de Requisição (CURL)

```bash
curl -X 'POST' \
  'http://localhost:8000/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "responses": [
    "Sim, ele grita comigo.",
    "Não temos problemas financeiros.",
    "Ele não gosta da minha família.",
    "Tenho medo dele.",
    "Ele já me empurrou."
  ]
}'
```

### APÊNDICE B - Configuração do Agente Especialista (Python)

```python
# Exemplo simplificado da classe SpecialistAgent
class SpecialistAgent(AgentWrapper):
    def __init__(self, agent_id: int, domain: str):
        super().__init__(
            name=f"Specialist_{agent_id}",
            system_message=get_specialist_prompt(agent_id, domain)
        )
        self.domain = domain

    async def analyze(self, user_input: str):
        # Lógica de chamada ao LLM
        response = await self.generate_reply(user_input)
        return self.parse_json(response)
```
