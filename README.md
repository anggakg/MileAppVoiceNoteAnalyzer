
# 🎙️ MileApp VoiceNote Analyzer 
Analisa dari voicenote MileApp, sebuah AI mini project 🤖 

Didukung oleh 🦙Llama dan 🦻Whisper





![Logo](https://apidoc.mile.app/themes/assets/img/mileapp.png)


## Features

- Auto detect voicenote (m4a) file in task data
- Auto analyze transcription into 
- Analisa mencakup:

            1. Ringkasan utama 
            2. Poin-poin penting 
            3. Topik utama yang dibahas
            4. Konteks dan implikasi penting
            5. Rekomendasi atau tindak lanjut (jika relevan)
- Light/dark mode toggle


## Reference

#### Tools yang digunakan

| Name | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| [Groq](https://groq.com/)      | **Inference** | Platform cloud AI yang sudah dilatih dan siap digunakan  |
| [Streamlit](https://streamlit.io/) | Interface | Free app builder web interaktif untuk data science dan machine learning |
| Whisper Large v3 Turbo | AI model | Digunakan untuk proses Speech-to-text voicenote |
| Llama 3.2 1B (Preview) 8k | AI model | Digunakan untuk analisa transcript dari audio |

#### Mengambil file audio dari MileApp task data

```http
  GET https://apiweb.mile.app/api/v3/task/{task_id}
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `Authorization` | `Token` | **Required**. Your Token API key. API key bisa didaptkan dengan panduan [Generate Access Token](https://apidoc.mile.app/#section/Authentication/Generate-access-token) |
| `task_id` | `string` | **Required**. Your task_id. Ambil task_id dari [menu Task dan klik View](https://doc.clickup.com/3837933/p/h/3n3zd-81962/aa00834626ae24f/3n3zd-82902) |





## Acknowledgements

 - Terinspirasi dari [Create Endtoend Personalize AI chatbot](https://dev.to/debapriyadas/create-an-end-to-end-personalised-ai-chatbot-using-llama-31-and-streamlitpowered-by-groq-api-3i32)
 - [Awesome README](https://github.com/matiassingers/awesome-readme)
 - 代码 100% 由 [Claude](https://claude.ai/) 创建 😉



## Authors

- [@ferritopia](https://www.github.com/ferritopia) - ide 🧠
- [@claude.ai](https://claude.ai/) - code 🤖

## Demo

https://mileappvn.streamlit.app/


## Appendix

### Limit penggunaan groqcloud

#### AI Audio Transcription

| Model | Requests per Minute | Requests per Day | Audio Seconds per Hour | Audio Seconds per Day |
| :-------- | :------- | :---------- | :---------- | :---------- |
| whisper-large-v3-turbo | 20 | 2000 | 7200 | 28.800 | 

#### AI Analyzer

| Model | Requests per Minute | Requests per Day | Tokens per Minute | Tokens per Day |
| :-------- | :------- | :---------- | :---------- | :---------- |
| llama-3.2-1b-preview | 30 | 7000 | 7000 | 500.000 | 


