# Deploying gradio demo

The demo is built as a Docker container and pushed to Docker Hub.

Then separately, there's a Huggingface Space repository which pulls that image when it's being built.

The image tag value is taken from the current local smashcima version.


## Deploy new tag version

1. Prepare the codebase to the desired point and `_version.py`
2. Test locally with `make demo-serve`
3. Build the docker image `make docker-demo-build`
4. Push the docker image `make docker-demo-push`
5. Open the HF Space files, edit the `Dockerfile` from browser, updating the the `FROM` statement to the new version
    - this can also be done by pulling and pushing using git, but since it's just a few characters, you can do it from the browser

The HF Space should now automatically rebuild and become live.


## Re-deploy the same tag version

1. Do the checklist above, but stop before editing the HF Space Dockerfile.
2. In the HF space `Settings`, click the `Factory rebuild` button.

Factory rebuild causes HF Docker image re-build, which triggers a new pull from Docker Hub. 
