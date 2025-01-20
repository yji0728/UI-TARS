# UI-TARS: Pioneering Automated GUI Interaction with Native Agents

## Overview
UI-TARS is a next-generation native GUI agent model designed to interact seamlessly with graphical user interfaces (GUIs) using human-like perception, reasoning, and action capabilities. Unlike traditional modular frameworks, UI-TARS integrates all key components—perception, reasoning, grounding, and memory—within a single vision-language model (VLM), enabling end-to-end task automation without predefined workflows or manual rules.

## Core Features
### Perception
- **Comprehensive GUI Understanding**: Processes multimodal inputs (text, images, interactions) to build a coherent understanding of interfaces.
- **Real-Time Interaction**: Continuously monitors dynamic GUIs and responds accurately to changes in real-time.

### Action
- **Unified Action Space**: Standardized action definitions across platforms (desktop, mobile, and web).
- **Platform-Specific Actions**: Supports additional actions like hotkeys, long press, and platform-specific gestures.

### Reasoning
- **System 1 & System 2 Reasoning**: Combines fast, intuitive responses with deliberate, high-level planning for complex tasks.
- **Task Decomposition & Reflection**: Supports multi-step planning, reflection, and error correction for robust task execution.

### Memory
- **Short-Term Memory**: Captures task-specific context for situational awareness.
- **Long-Term Memory**: Retains historical interactions and knowledge for improved decision-making.

## Capabilities
- **Cross-Platform Interaction**: Supports desktop, mobile, and web environments with a unified action framework.
- **Multi-Step Task Execution**: Trained to handle complex tasks through multi-step trajectories and reasoning.
- **Learning from Synthetic and Real Data**: Combines large-scale annotated and synthetic datasets for improved generalization and robustness.

## Training Pipeline
1. **Pre-Training**: Leveraging large-scale GUI-specific datasets for foundational learning.
2. **Supervised Fine-Tuning**: Fine-tuning on human-annotated and synthetic multi-step task data.
3. **Continual Learning**: Employing online trace bootstrapping and reinforcement learning for continual improvement.

## Evaluation Metrics
- **Step-Level Metrics**: Element accuracy, operation F1 score, and step success rate.
- **Task-Level Metrics**: Complete match and partial match scores for overall task success.
- **Other Metrics**: Measures for execution efficiency, safety, robustness, and adaptability.

## Deployment

### Cloud Deployment
We recommend using HuggingFace Inference Endpoints for fast deployment.
We provide two docs for users to refer:

English version: [GUI Model Deployment Guide](https://juniper-switch-f10.notion.site/GUI-Model-Deployment-Guide-17b5350241e280058e98cea60317de71)

中文版: [GUI模型部署教程](https://bytedance.sg.larkoffice.com/docx/TCcudYwyIox5vyxiSDLlgIsTgWf#U94rdCxzBoJMLex38NPlHL21gNb)


### Local Deployment [vLLM]
We recommend using vLLM for fast deployment and inference. You need to use `vllm>=0.6.1`.
```bash
pip install -U transformers
VLLM_VERSION=0.6.6
CUDA_VERSION=cu124
pip install vllm==${VLLM_VERSION} --extra-index-url https://download.pytorch.org/whl/${CUDA_VERSION}

```
#### Start an OpenAI API Service

Run the command below to start an OpenAI-compatible API service:

```bash
python -m vllm.entrypoints.openai.api_server --served-model-name ui-tars --model <path to your model>
```

Then you can use the chat API as below with the gui prompt (choose from mobile or computer) and base64-encoded local images (see [OpenAI API protocol document](https://platform.openai.com/docs/guides/vision/uploading-base-64-encoded-images) for more details):

- Prompt template for mobile:
```python
## Below is the prompt for mobile
prompt = r"""<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task. 

## Output Format
```\nAction_Summary: ...
Action: ...\n```

## Action Space
click(start_box='<|box_start|>(x1,y1)<|box_end|>')
long_press(start_box='<|box_start|>(x1,y1)<|box_end|>', time='')
type(content='')
scroll(direction='down or up or right or left')
open_app(app_name='')
navigate_back()
navigate_home()
WAIT()
finished() # Submit the task regardless of whether it succeeds or fails.

## Note
- Use English in `Action_Summary` part.

## User Instruction
"""

- Prompt template for computer:
```python
## Below is the prompt for computer
prompt = r"""<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task. 

## Output Format
```\nThought: ...
Action: ...\n```

## Action Space

click(start_box='<|box_start|>(x1,y1)<|box_end|>')
left_double(start_box='<|box_start|>(x1,y1)<|box_end|>')
right_single(start_box='<|box_start|>(x1,y1)<|box_end|>')
drag(start_box='<|box_start|>(x1,y1)<|box_end|>', end_box='<|box_start|>(x3,y3)<|box_end|>')
hotkey(key='')
type(content='') #If you want to submit your input, use \"\
\" at the end of `content`.
scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', direction='down or up or right or left')
wait() #Sleep for 5s and take a screenshot to check for any changes.
finished()
call_user() # Submit the task and call the user when the task is unsolvable, or when you need the user's help.


## Note
- Use Chinese in `Thought` part.
- Summarize your next action (with its target element) in one sentence in `Thought` part.

## User Instruction
"""
```

- Inference codes:
```python
import base64
from openai import OpenAI


instruction = "search for today's weather"
screenshot_path = "screenshot.png"
client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="empty",
)

## Below is the prompt for mobile
prompt = r"""<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task. 

## Output Format
```\nAction_Summary: ...
Action: ...\n```

## Action Space
click(start_box='<|box_start|>(x1,y1)<|box_end|>')
long_press(start_box='<|box_start|>(x1,y1)<|box_end|>', time='')
type(content='')
scroll(direction='down or up or right or left')
open_app(app_name='')
navigate_back()
navigate_home()
WAIT()
finished() # Submit the task regardless of whether it succeeds or fails.

## Note
- Use English in `Action_Summary` part.

## User Instruction
"""

with open(screenshot_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
response = client.chat.completions.create(
    model="ui-tars",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt + instruction},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_string}"}},
            ],
        },
    ],
    frequency_penalty=1,
    max_tokens=128,
)
print(response.choices[0].message.content)


```
### Local Deployment [Ollama]
Ollama can deploy the model via gguf format. Bugs exist for safetensors.

#### Convert from safetensors to gguf
We convert the model into gguf format by using the script from [llama.cpp](https://github.com/ggerganov/llama.cpp/blob/master/convert_hf_to_gguf.py):

```bash
python3 convert_hf_to_gguf.py <path to your model>
```

The gguf file will be generated under the path provided.

#### Deploy gguf model
We deploy the model by following Ollama [tutorial](https://github.com/ollama/ollama?tab=readme-ov-file#customize-a-model).

```bash
# Create Modelfile, Windows users can just create a file named Modelfile
echo "FROM ./path/to/model.gguf" > Modelfile

# Create model in Ollama
ollama create ui-tars -f Modelfile

# Run the model
ollama run ui-tars

```

Test script is same as vLLM except two changes:

```python
...
client = OpenAI(
    base_url="http://127.0.0.1:11434/v1/",
    ...
)
...
response = client.chat.completions.create(
    model="ui-tars" # the name we create via Ollama cli
    ...
)

```


## License
UI-TARS is licensed under the Apache License 2.0.

## Acknowledgements
This project builds upon and extends the capabilities of Qwen-2-VL, a powerful vision-language model, which serves as the foundational architecture for UI-TARS. We would like to acknowledge the contributions of the developers and researchers behind Qwen-2-VL for their groundbreaking work in the field of multimodal AI and for providing a robust base for further advancements.

Additionally, we thank the broader open-source community for their datasets, tools, and insights that have facilitated the development of UI-TARS. These collaborative efforts continue to push the boundaries of what GUI automation and AI-driven agents can achieve.