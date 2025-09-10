# posture-correction-backend

Backend for the posture correction system

- Estimates the user’s neck angle from smartphone sensor data and front camera images.
- To use the system, see [Usage](#usage).
- To set up the system locally, see [Setup](#setup).
- If you only want to use the model, you can download it from [Pretrained Models](https://drive.google.com/drive/folders/14OG010mwTi0XLHKoFhliflH6sxUvWVX1?usp=sharing).

# Structure

- `api` (FastAPI) and `db` (MySQL) are placed in Docker Compose.
- Uses the local GPU for inference (`nvidia/cuda:12.1.1`).

**Ports used in development**

| Service    | Port | Notes               |
| ---------- | ---- | ------------------- |
| FastAPI    | 3330 | API                 |
| MySQL      | 3331 | Database            |
| PHPMyAdmin | 3332 | Database Management |

## API

### OpenAPI

It is public on [DockerHub](https://hub.docker.com/repository/docker/kntwt/posture-correction-schema/general), so please refer to it as needed (you can also check it at `http://localhost:3330/docs` after starting the API).  
By pulling it during frontend development, you can call the API with type safety.

### User-related

- **User registration**
  - You can create a new account using Basic authentication or an email address (each has a different endpoint).
- **Calibration**
  - Calibration is required for more accurate estimation per user.
  - Please keep your neck straight during calibration so that the smartphone angle and your face angle are aligned as much as possible.
- **Accessing information**
  - To access user-related information, you need to include the JWT Token (issued after login) in the Cookie when making requests.
  - The token is embedded in the Cookie at login, so just use it directly.

### Posture estimation

- Posture estimation requires both the smartphone gyroscope data and the front camera image.
- To access posture estimation or historical posture data, the Cookie must include user info (JWT Token), and the Header must include an `appId`.
  - The Header key can be `app-id` or `app_id` (case-insensitive).
- Calibration (recording the most correct posture in advance) is required for posture estimation of logged-in users.
- For guest users, the endpoint `/posture/estimate/guest` can be used without calibration.
- If you only want feedback on the face angle before calibration, use `/posture/estimate/feature`.

## Database

- MySQL is used as the database.
- See `db/init/1_create_table.sql` for the table schema.

# Setup

## Environment Variables

Copy `.env.sample`, and replace the values enclosed in `<>` with appropriate values.

    cp .env.sample .env

- `ESTIMATE_BODY_POSE_POOL_COUNT` and `ESTIMATE_HEAD_POSE_POOL_COUNT` are the number of processes allocated to feature extraction (skeleton estimation and head pose estimation) used for neck angle estimation. Adjust according to your environment.
- `MOCK_SECRET_KEY` and `TRAIN_IF_NOT_EXIST` are for workflow purposes, so do not change their default values during development.

## Posture Estimation

- The skeleton estimation library used is [Pytorch-OpenPose](https://github.com/Hzzone/pytorch-openpose). Run `git submodule init` and `git submodule update`, then place the model under `api/pytorch-openpose/model` according to the repository’s README.
- If no neck angle estimation model is found at startup, training will run automatically. Place the [required training data](https://drive.google.com/drive/u/0/folders/1DCPd7bjqo80g9JaEFJEANtliDxzXwIs_) under `api/estimators/data` (do not rename the files).
- After running posture estimation, the original image, head pose estimation results, and skeleton estimation results will be output to `api/images` (or the directory specified in environment variables)/`:userId`/`(original|head|neck)`.

## User Authentication

- Public and private keys are used for JWT signing. Place the keys encrypted in `EdDSA` format under `api/configs/keys` (`secret_key`, `publick_key.pub`).
- The key used for signing Cookies can be changed via environment variables.

## Run Application

Run the following command in the project root directory:

```sh
make docker-build-prod
```

**use prod configuration even if you are in development environment.**
