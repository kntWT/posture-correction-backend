# posture-correction-backend

Backend for the posture correction system\

- Estimates the user's neck angle from smartphone sensor information and the front camera image.
- If you want to use the system, please refer to [Usage](#usage).
- If you want to set up the system locally, please refer to [Setup](#setup).

# Configuration

- `api` (FastAPI) and `db` (MySQL) are deployed via Docker Compose.
- Inference is performed using the local GPU (nvidia/cuda:12.1.1).

**List of ports used in development**

| Service Name | Port Number | Note                |
| ------------ | ----------- | ------------------- |
| FastAPI      | 3330        | API                 |
| MySQL        | 3331        | Database            |
| PHPMyAdmin   | 3332        | Database Management |

## API

### OpenAPI

It is public on [DockerHub](https://hub.docker.com/repository/docker/kntwt/posture-correction-schema/general), so please refer to it as needed (Once the API is running, you can also view it at `http://localhost:3330/docs`).
Pulling this during frontend development allows for type-safe API calls.

### User Related

- User Registration
  - You can create a new user via Basic Authentication or email address (endpoints differ for each).
- Calibration
  - Calibration is required to perform more accurate estimation for each user.
  - Please perform calibration with your neck straight, keeping the smartphone angle and your face angle as aligned as possible.
- Access to Information
  - To access user information, you need to include the JWT Token issued after login in the Cookie of your request.
  - It is embedded in the Cookie upon login, so please use it as is.

### Posture Estimation

- Posture estimation requires the smartphone's gyro sensor and the image from the front camera.
- To access posture estimation or past posture data, the Cookie must contain user information (JWT Token) and the Header must contain the `appId`.
  - The Header key should be `app-id` or `app_id` (case-insensitive).
- Calibration is required beforehand for posture estimation of logged-in users.
- Calibration is not required for the guest user endpoint (`/posture/estimate/guest`).
- If you want to feed back only the user's face angle before calibration, please use `/posture/estimate/feature`.

## Database

- MySQL is used for the database.
- Please refer to `db/init/1_create_table.sql` for the table schema.

# Usage

- Please log in at [App Registration](https://vps8.nkmr.io/posture-correction-app-request), select the server to use, and create a project.
  - Note the `appId` displayed after creation and include it in the Header when making API requests.
- Connect to the server (or local machine) via VPN using [Tailscale](https://tailscale.com/) or similar.
- The API can be used by proxying on the HTTP server of the destination and connecting to `<Destination IP>:3330/`.
- Please refer to [API Configuration](#api) and call the API appropriately (pay attention to SSL and CORS).
- Note that Docker may go down if the connection destination (the host machine running this backend) is not operated for a long time.

# Setup

## Environment Variables

Copy `.env.sample` and change the values enclosed in `<>` to appropriate values.

```sh
cp .env.sample .env
```

- `ESTIMATE_BODY_POSE_POOL_COUNT` and `ESTIMATE_HEAD_POSE_POOL_COUNT` are the number of processes assigned to feature extraction (skeleton estimation and head pose estimation) used for neck angle estimation, respectively. Set appropriate values according to the operating environment.
- `MOCK_SECRET_KEY` and `TRAIN_IF_NOT_EXIST` are variables for workflow, so please do not change them from the default values during the development stage.

## Posture Estimation

- [Pytorch-OpenPose](https://github.com/Hzzone/pytorch-openpose) is used as the skeleton estimation library for posture estimation. After running `git submodule init` and `git submodule update`, place the model under `api/pytorch-openpose/model` according to the repository's README.
- If the neck angle estimation model does not exist at startup, training will run, so please place the [data required for training](https://drive.google.com/drive/u/0/folders/1DCPd7bjqo80g9JaEFJEANtliDxzXwIs_) under `api/estimators/data` (do not change the file names).
- After posture estimation is executed, the original image, head pose estimation result, and skeleton estimation result are output to `api/images (or the directory specified by the environment variable)/:userId/(original|head|neck)`, respectively.

## User Authentication

- Public and private keys are used for JWT signing. Please place the keys encrypted in `EdDSA` format in `api/configs/keys` (`secret_key`, `publick_key.pub`).
- The key used to sign the Cookie can be changed via environment variables.
