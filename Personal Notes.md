# Personal Notes

## Week 1 Introduction to Coding LLMs and AI Development

- 对于软件开发工程师来说，在AI时代，我们需要阅读更多的代码，提高识别代码坏味道的嗅觉

- LLMs(large language models) 是一个基于下一个输入的自回归的模型。比如：假设AI回复“以下是提供的例子”，这段话的概率P等于 P(以)*P(下|以)*P(是|以下)*P(提|以下是)*P(供|以下是提)*P(的|以下是提供)*P(例|以下是提供的)*P(子|以下是提供的例)

- 有明确的技巧修改prompt，可以显著提高LLM的结果：

  - Zero-shot prompting: 没有例子，没有引导

  - K-shot prompting: 在Prompt中提供几个例子供AI参考，通常值为1, 3, 5，适合不需要太多推理的任务

    ```
    Write a for-loop iterating over a list of strings using the naming convention in our repo. Here are some examples of how we typically format variable names.
    
    <example>
    var StRaRrAy = [‘cat’, ‘dog’, ‘wombat’]
    </example>
    
    <example>
    def func CaPiTaLiZeStR = () => {}
    </example>
    ```

  - Chain-of-Thought Prompting: Multi-shot CoT（多样本思维链）：提供例子，例子中包含推理轨迹；Zero-shot CoT（零样本思维链）：不需要给例子，末尾添加：Let’s think step-by-step；显式标签：让AI把推理过程放在<reasoning>标签内；适用场景：多步逻辑任务，比如编程或者数学

    ```
    # Multi-shot CoT
    
    I want to write a function to check if a number is a perfect cube and a perfect square. Make sure to provide your reasoning first. Here are some examples of how to  provide reasoning for a coding task.
    
    <example>
    Write a function that finds the maximum element in a list.
    Steps: Initialize a variable with the first element. Traverse the list, comparing…
    </example>
    
    <example>
    Write a function that checks is a number is a palindrome
    Steps: Take the number. Reverse the elements in the numbers. Check if …
    </example>
    ```

    ```
    # Zero-shot CoT
    
    Write a function to find the longest increasing subsequence in an array.
    
    Think step by step about the subproblems before coding. Include worked out examples of subarrays you are considering as you answer this question.
    ```

  - Self-consistency Prompting: 输入多次Prompt（人工或者自动化），选取出现概率最高的那个结果

  - Tool Use: 允许AI调用外部工具， 避免生成过时结果或者幻觉

    ```
    Fix the IndexError. Ensure the CI tests still pass once you have made the fix. Here are the available tools. 
    
    <tools>
    pytest -s /path/to/unit_tests
    
    pytest -v /path/to/integration_tests
    </tools>
    ```

  - Retrieval Augmented Generation: AI回答问题前会去外部数据库搜索相关资料，并一起喂给AI，用于降低训练成本，减少幻觉

    ```
    I want to extend the UserAuthService class to check that the client provides a valid OAuth token. 
    
    Here is how the UserAuthService works now:<code_snippet>
    def issue_oauth_token():
    	….
    </code_snippet>
    
    Here is the path to the requests-oauthlib documentation:<url>
    https://requests-oauthlib.readthedocs.io/en/latest/
    </url>
    ```

  - Reflexion: LLM可以反思提供的输出是否正确，可以在Prompt后添加`Now critique your answer. Was it correct? If not, explain why and try again`

- 原则：使用标准的结构化语言作为Prompt，方便AI识别具体的部分以免混淆指令和拷贝的内容，比如：

  ```
  Here are the logs:
  <log>
  LOG MESSAGE
  <log>
  and the stack trace:
  <error>
  STACK TRACE
  <error>
  ```

  

- 

  

  ### 思考：为什么有时候同样的输入输出不同？

- ### 它是“抽样”而非“确定”

  图片中的公式 $P(x_t | x_1, \dots, x_{t-1})$ 计算出的是一个**概率分布**。

  例如，输入“床前明月”，模型预测下一个词的概率可能是：

  - **光**: 90%
  - **亮**: 5%
  - **地**: 3%
  - ...其他: 2%

  如果模型永远只选概率最高的那一个（这叫 **Greedy Decoding，贪婪搜索**），它的输出确实会一模一样。但这样生成的文本往往非常呆板、重复，缺乏“灵气”。

- ### 温度 (Temperature) 的魔法

  在你提供的代码中有一行：

  ```
  options={"temperature": 0.5}
  ```

  **Temperature** 是控制 AI “创造力”或“随机性”的旋钮，会影响概率分布曲线：

  - **低温度 ($< 0.5$)**：模型会变得保守，更倾向于选概率最高的词。输出比较稳定，适合数学计算、代码生成或你现在的字符串反转任务。
  - **高温度 ($> 1.0$)**：模型会给那些“低概率”的词更多机会。这会让 AI 更有创意，但也更容易“胡说八道”。

- 随机数种子

  #### **种子 (Seed) 负责执行“抽样”**

  一旦概率分布确定了，电脑需要“掷一次骰子”来决定选哪一个。

  - 电脑里的随机数其实是“伪随机”。如果你给一个固定的 **Seed**，每次掷骰子的结果序列就是**一模一样**的。
  - **如果没有 Seed**：即便温度是 0.5（概率分布固定），每次掷骰子选中的词可能还是不一样。
  - **如果有 Seed**：只要概率分布（温度）不变，每次选中的词就完全一样
  - 

你看到的“不一样”，是因为 AI 开发者的设计初衷是让它**模拟人类的随机感**。但在做这种**“硬逻辑”**（比如反转字符串）的作业时，这种随机性反而成了障碍。

这也是为什么 CS146S 强调**测试多次 (`NUM_RUNS_TIMES = 5`)** 的原因——如果你的 Prompt 足够好，它应该能在随机性的干扰下，依然有高概率命中正确答案。



