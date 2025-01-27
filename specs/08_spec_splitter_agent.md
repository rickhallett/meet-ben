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
   35 The high level goal is to create a new TextSplitter LLM Node that is responsible for taking large queries from the user and breaking them up into chunks that can be passed to the Tagger agent for tag associa      tion, and then eventually to the UpdateKnowledgeStore Agent responsible for creating the right embeddings and storage in postgres db.
   36
   37 ## Mid-Level Objective
   38
   39 - [List of mid-level objectives - what are the steps to achieve the high-level objective?]
   40 - [Each objective should be concrete and measurable]
   41 - [But not too detailed - save details for implementation notes]
   42
   43 CREATE TextSplitter LLM Node (follow Tagger as an example of the api)
   44 CREATE text_splitter.j2 prompt that instructs the TextSplitter LLM call that it is to divide the provided text into chunks between min and max words, using these parameters as a range in which to find a cohe      rent cut off point.
   45 CREATE large_query.json in the data directory with an example of a full ACT clinical assessment (written in free hand, unstructured form) to represent the user uploading a large amount of information in one       request. Follow the json api as defined in requests/events/request.json (read-only)
   46 CREATE def test_text_splitter(large_query: str) -> None in llm_playground.py to test the functioning of TextSplitter (check other tests for general workflow). Check the agent is able to split the chunks into       varying lengths between min and max, and that it splits along complete sentences (i.e. always finishes with a period).
   47
   48 ## Implementation Notes
   49 - [Important technical details - what are the important technical details?]
   50 - [Dependencies and requirements - what are the dependencies and requirements?]
   51 - [Coding standards to follow - what are the coding standards to follow?]
   52 - [Other technical guidance - what are other technical guidance?]
   53
   54 ## Beginning Context
   55 /read-only app/pipelines/process_event/tagger.py
   56 /read-only app/prompts/generate_tags.j2
   57 /read-only playground/llm_playground/py
   58 /read-only requests/events/request.json
   59 /add app/pipelines/process_event/chunk_splitter.py
   60
   61 ### Ending context··
   62 app/pipelines/process_event/chunk_splitter.py
   63 app/prompts/chunk_splitter.j2
   64
   65 ## Low-Level Tasks
   66 > Ordered from start to finish
   67
   68 Please breakdown this problem into a series of tasks that can be completed in a single step, using the following format:
   69
   70 1. [First task - what is the first task?]
 Normal  /private/var/folders/wb/71c0kjcd56z1ll3j2p_6y_gc0000gn/T/tmpqr2wuc55.md[+]                                                                                                   markdown utf-8[unix] 0B  55:48