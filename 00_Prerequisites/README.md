# 0 - Prerequisites

이번 단계에서는 Python과 Boto3 라이브러리를 이용하여 AWS Bedrock 서비스에 접근 하는 테스트용 코드들을 작성하였다.
이 코드는 N.Virginia(us-east-1) 리전 대상으로 작성한 코드이며 [완성 된 코드](bedrock_basic.py)를 참고하면 된다.

## CHECK
완성 된 코드를 정상적으로 돌리기 위해선 아래의 사항을 만족해야 한다

- 로컬에 AssumeRole 정책을 가진 AWS 프로필이 설정되어 있어야 한다.
- AssumeRole 하기 위한 Role 이 생성되어 있어야 한다.
- us-east-1 리전의 Bedrock 서비스에 Titan Text G1 - Express 모델에 대한 접근 설정이 되어 있어야 한다.

## SETTING

### 프로젝트 환경 설정
- python -m venv env_name 으로 가상환경 생성한다
- source env_name/bin/activate 로 가상환경 활성화
- pip install --no-build-isolation "boto3>=1.35" "awscli>=1.36" "botocore>=1.35" 로 boto3, botocore, awscli를 설치한다

### 코드 수정 (bedrock_basic.py)
- YOUR_AWS_PROFILE_NAME 의 값을 로컬에 설정한 프로필 값으로 변경한다
- YOUR_AWS_ACCOUNT_ID 의 값을 AWS Account ID 값으로 변경한다
- YOUR_ASSUME_ROLE_NAME 의 값을 ASSUME 할 Role의 이름으로 변경한다