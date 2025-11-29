# Use AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies
RUN yum install -y gcc gcc-c++ && yum clean all

# Copy requirements and install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy model files
COPY purchase_model.pkl ${LAMBDA_TASK_ROOT}
COPY scaler.pkl ${LAMBDA_TASK_ROOT}

# Copy Lambda function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "lambda_function.lambda_handler" ]
