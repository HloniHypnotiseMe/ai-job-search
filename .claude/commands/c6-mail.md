# /c6-mail - Send a Career Communication Through C6 Mail

Use this command when the user explicitly asks to send a career-related email.

## Non-negotiable

C6-Mail-Services is the mail boundary. Do not route career mail through Gmail, Notion, or a new SMTP implementation.

Endpoint:
- POST /api/v1/mail/send

Authentication:
- X-C6-Mail-Key

Payload:
- to: string[]
- subject: string
- text: string
- optional html
- optional reply_to

The base URL and API key are runtime secrets/configuration:
- C6_MAIL_BASE_URL
- C6_MAIL_API_KEY

## SOP/SOMS

Before sending:
1. Audit the application record and exact submitted materials.
2. Capture the communication evidence and intended outcome.
3. Diagnose what communication is required.
4. Recommend the draft.
5. User explicitly selects/approves the send.
6. Execute through C6-Mail-Services.
7. Measure the service response and capture message_id.
8. Re-audit the application state.
9. Prove the communication was accepted by the mail service.

Never invent claims about the candidate, employer, interview stage, salary, or prior communication.
Never send automatically from a passive signal.
