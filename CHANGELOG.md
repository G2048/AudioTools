## 0.2.0 (2025-03-16)

### Feat

- **adapters**: add recongizers package; add LocalNeuralAudioRecognizer adapter
- **interfaces**: add the AudioRecognizerInterface
- **configs**: add the NeuralSettings for local llm model
- **adapters**: add the senders adapters package; move on emails to adapters/senders
- **converter**: add conver a file to numpy array
- **converter**: full converter
- **converter**: full converter
- **transcriber**: full transcriber audio; not only first 30 seconds
- **audio**: add converter, uploader and trascribtion audio
- **audio**: upload file
- **buckets**: add choose path for upload file
- **aws**: add base package for manipulation of aws and service
- **configs**: add settings for aws
- **services**: add transcibation of upload audio file
- **webui**: remove footer, add Title
- **webui**: add alternative constructor for mount multiply pages
- **webui**: change theme for audio page to standart
- **pages**: add recive email messages to audio page
- **emails**: sending batch emails
- **emails**: add class for sending email via smtp
- **configs**: add settings for emails
- add template of ui pages for projects
- create simple test ui

### Fix

- **configs/log_settings**: disorder log_id from different threads
- **configs/log_settings**: set app_name for logger
- **adapters**: change AudioUploader to AudioAwsUploader; change import from the services package to adapters
- **uploader**: inheritance S3File from FileInterface and AwsUploader from UploaderInterface; change imports to interfaces package
- **converter**: return full numpy array after convert audio to np.array
- **converter**: AudioConverter has not method file_path
- **buckets**: wrong upload dir
- **backets**: NameError: name 'logger' is not defined
- **buckets**: cannot find methods for s3client

### Refactor

- **configs/settings**: change the get_appsettings function to get_app_settings
- **configs/pyproject**: add special class ParserPyproject for parsin data from pyproject.toml
- **pages/converter**: reduce algoritm for convertation file to a format
- **interfaces**: rename abstractmethod from execute to upload for AudioUploaderInterface
- **services**: remove AudioRecognizer; replace it on LocalNeuralAudioRecognizer
- **pages**: change recoginzer to AudioRecognizerInterface for transcribe page
- **pages**: remove AudioRecognizer class from transcribe page
- **AudioUploader**: move on AudioUploader to adapters/uploaders/
- **SenderInterface**: change title property to type
- **AudioTranscribePage**: invert class dependencies to interfaces
- **webui**: change the location of the Page interface
- **services**: remove the interface module
- **drivers**: move on email's classes to the low-level package drivers
- **interfaces**: move interfaces to a separate package
