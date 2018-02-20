# AlexaOps - Controlling AWS using Alexa
_Why? cause why not?!_

# Intro

This repo is an example implementation backed by a [presentation](https://chrislennon.github.io/AlexaOps-Presentation/). The idea is to create an Alexa skill, backed by AWS Lambda to control various operations on the AWS platform.

# Usage

This skill supports the following actions:

- "How many development servers are running?"
    - `There are 3 Development servers, 1 server is offline`
- "Turn on all development servers"
    - `I have started 1 development server`
- "What is my Amazon bill?"
    - `Your current total is $5. Your itemised bill shows, Route53 - $3, DynamoDB - $2`
- "Scale my backend service to 5"
    - `I have scaled the backend service to 5 instances`

# Setup

Steps are covered in the 'AlexaOps' (final) section of the [presentation](https://chrislennon.github.io/AlexaOps-Presentation/) however are also covered below in less detail.

- Create a new skill in the [Alexa Developer console](https://developer.amazon.com/edw/home.html#/).
- Take note of the skill id in the created skill.
- Create intents, slots and utterances - `alexa_template.json` can be copied into the code editor.
- Change `ALEXA_SKILL_ID` in the `serverless.yml` to the above value.
- Run `serverless deploy`
- Take note of the created function's ARN.
- In the Alexa developer console add the lambda endpoint ARN.
- Check the skill is enabled within your account in the [Alexa App](https://alexa.amazon.com/)

# Presentation

The initial revision of the presentation is available on [GitHub pages](https://chrislennon.github.io/AlexaOps-Presentation/)
