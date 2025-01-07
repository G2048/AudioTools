## Audio Transcriber

This is a simple UI transcriber that uses Whisper to transcribe audio files.

## Requirements

- Docker
- Docker Compose
- Whisper

## Installation

1. Clone the repository
2. Clone the Whisper model (e.g., `git clone https://huggingface.co/openai/whisper-medium`)
3. Move the Whisper model to the `.whisper` directory
4. Copy the `env.example` file to `.env`
5. Edit the `.env` file to include your Whisper model
6. Run `docker-compose up -d`
7. Open the UI in your browser at `http://localhost:8000`

## Usage

1. Select the audio file you want to transcribe
2. Click the "Transcribe" button
3. Wait for the transcription to complete
4. The transcription will be displayed in the UI

## TODO List

- [ ] Add Telegram bot integration
- [ ] Create a single microservice for AI-transcription
- [x] Add Broker for Microservices
- [x] [Add Sender Email microservice](https://github.com/G2048/EmailSender.git)
- [ ] Add the Whisper Transcriber Microservice
- [ ] Add Sender Telegram microservice
- [ ] Add TTS

## Contributing

Contributions are welcome! If you find a bug or have a suggestion, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
