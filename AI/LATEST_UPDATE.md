# Latest update


Changes applied:

- Explanation questions no longer start the job questionnaire.
- `Can u explain for me an internship for university student` goes to the normal response router and then OpenRouter when no suitable saved answer exists.
- `What is an internship?` bypasses the generic internship search-tip row in `bot_responses.csv`.
- Vacancy questions such as `Is there any job for computer science?` and `What are available jobs for computer science?` start the guided flow.
- Generic words such as `university student` are no longer extracted as a programme/major.
- A separate question asked during the guided flow is answered without deleting the saved job-flow state.
- The selected OpenRouter model remains `nvidia/nemotron-3-ultra-550b-a55b:free`.
- Real `.env` files, local virtual environments, IDE settings, and cache files are excluded from the archive.

Privacy cleanup:

- Existing local account rows, plaintext passwords, and conversation history were not copied into this distributable build.
- `data/users.csv` and `data/conversation_log.csv` are created locally at runtime and are ignored by Git.
