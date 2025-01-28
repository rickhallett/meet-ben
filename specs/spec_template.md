1 # Specification Template
    2 > Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.
    3
    4 ## High-Level Objective
    5
    6 - These two mermaid diagrams demonstate the overall application flow and how pipelines and nodes are connected.
    7
    8 ```mermaid
    9 graph TD
   10     subgraph Docker Compose
   11         Source[Source<br>Event Data] -- HTTP Request --> Backend[Backend<br>FastAPI]
   12         Backend --> DB[Database<br>PostgreSQL]
   13         Backend -->|Sync| Pipeline1[Pipeline<br>Process Event]
   14         DB --> Pipeline1
   15         Backend -->|Queue Task| Broker[Broker<br>Redis]
   16         Broker -->|Async| QueueWorker[Queue Worker<br>Celery]
   17         QueueWorker --> Pipeline2[Pipeline<br>Process Event]
   18     end
   19 ```
   20
   21 Pipeline example:
   22
   23 ```mermaid
   24 graph TD
   25     subgraph Pipeline_Example
   26         Event["Event: TaskContext"] --> AnalyzeTicket["Node (LLM): AnalyzeTicket"]
   27         AnalyzeTicket --> TicketRouter["Node (Router): TicketRouter"]
   28         TicketRouter --> GenerateResponse["Node (LLM): GenerateResponse"]
   29         GenerateResponse --> SendReply["Node: SendReply"]
   30         TicketRouter --> EscalateTicket["Node: EscalateTicket"]
   31         TicketRouter --> ProcessInvoice["Node: ProcessInvoice"]
   32     end
   33
   34 ```
   35
   36 ## Mid-Level Objective
   37
   38 - [List of mid-level objectives - what are the steps to achieve the high-level objective?]
   39 - [Each objective should be concrete and measurable]
   40 - [But not too detailed - save details for implementation notes]
   41
   42 ## Implementation Notes
   43 - [Important technical details - what are the important technical details?]
   44 - [Dependencies and requirements - what are the dependencies and requirements?]
   45 - [Coding standards to follow - what are the coding standards to follow?]
   46 - [Other technical guidance - what are other technical guidance?]
   47
   48 ## Beginning Context
   49
   50 ### Ending context··
   51
   52 ## Low-Level Tasks
   53 > Ordered from start to finish
   54
   55 Please breakdown this problem into a series of tasks that can be completed in a single step, using the following format:
   56
   57 1. [First task - what is the first task?]
   58 ```aider
   59 What prompt would you run to complete this task?
   60 What file do you want to CREATE or UPDATE?
   61 What function do you want to CREATE or UPDATE?
   62 What are details you want to add to drive the code changes?
   63 ```
   64 2. [Second task - what is the second task?]
   65 ```aider
   66 What prompt would you run to complete this task?
   67 What file do you want to CREATE or UPDATE?
   68 What function do you want to CREATE or UPDATE?
   69 What are details you want to add to drive the code changes?
   70 ```
   71 3. [Third task - what is the third task?]
   72 ```aider
   73 What prompt would you run to complete this task?
   74 What file do you want to CREATE or UPDATE?
 Normal  /private/var/folders/wb/71c0kjcd56z1ll3j2p_6y_gc0000gn/T/tmpqr2wuc55.md[+]                                                                                                   markdown utf-8[unix] 0B  33:1
19 fewer lines