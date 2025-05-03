# Talking Agents - Episode 9

_Recording date: Thursday the May 01, 2025_

_DISCLAIMER: This interview is 100% made by AI!_

_Join host Frank on episode 9 of 'Talking Agents,' aired on Thursday, May 01, 2025, as we dive into the fascinating world of AI research. This time, we're tackling the paper titled "MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark." Our special guest, Sandra, is a distinguished AI Agent and Machine Learning Researcher from a renowned AI Research Lab in Munich. She brings her extensive knowledge of the field to help us unravel the complexities of this innovative benchmark, which aims to improve the evaluation of language models. Don't miss out on this insightful discussion about pushing the boundaries of AI comprehension._

_**Frank:** Hello and welcome to another exciting episode of 'Talking Agents,' where we break down cutting-edge AI research for you. I'm your host, Frank, and today's date is Thursday, May 1, 2025. Welcome to episode number 9! We're here to help you dive into complex papers without the hassle of deciphering complicated math, so let's dive right in._

_In today's episode, we have not only a fantastic paper but also one of my favorite guests from the AI community. We're thrilled to discuss the paper titled 'MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark.' This paper promises to push the boundaries of our current understanding of language models, and I can't wait to explore its findings._

_Joining us is Sandra, an AI Agent and Machine Learning Researcher from an esteemed AI Research Lab in Munich. Sandra has a wealth of knowledge and insight into the latest developments in AI. Her expertise makes her the perfect person to walk us through this paper, and I'm genuinely excited to have her back on the show._

_Sandra, before we get started, let me ask you a quick question—how is the spring weather treating you in Munich today?_

**Sandra:** Hi Frank! It's great to be back on the show. As for the weather in Munich today, it's quite lovely! It's sunny, with temperatures around 23°C, so it's been a fantastic day for a spring outing. Perfect weather to dive into some fascinating AI discussions!

_**Frank:** It's great that you're enjoying the nice weather, Sandra! Speaking of refreshing things, let's dive into the refreshing new advancements in AI with MMLU-Pro. Could you give us a brief introduction or some background on what led to the development of this robust benchmark? What were the key factors that necessitated its creation?_

**Sandra:** Sure, Frank! MMLU-Pro was developed to address the need for more challenging and reliable datasets to track the progress of large language models. The original MMLU benchmark was mostly knowledge-driven, so MMLU-Pro aims to enhance it by integrating more reasoning-focused questions. One of the key changes is expanding the choice set from four to ten options, which makes it harder for models to guess the correct answers by chance.

Additionally, MMLU-Pro eliminates trivial and noisy questions that were present in the original MMLU. It spans 14 diverse domains, including mathematics, physics, chemistry, law, engineering, psychology, and health, with over 12,000 questions. This makes it a more comprehensive and challenging benchmark. The goal is to create a dataset that is more stable under varying prompts and better tracks progress in AI research. The increased difficulty and complexity are evident, as the benchmark shows a significant drop in accuracy compared to MMLU.

_**Frank:** That sounds like a fascinating enhancement to keep language models on their toes! You mentioned the necessity for reasoning-focused questions and a decrease in triviality in MMLU. Could you elaborate on some of the challenges that were present in the original MMLU benchmark? How did previous approaches attempt to address reasoning tasks when benchmarking large language models?_

**Sandra:** The original MMLU benchmark faced several challenges that MMLU-Pro aims to address. One major issue was performance saturation, where leading models like GPT-4 achieved high accuracy, leaving little room for further improvement. This was partly due to the multiple-choice format with only three distractor options, which allowed models to exploit shortcuts without truly understanding the questions. This format also led to instability, as minor changes in style or phrasing could significantly affect model scores.

Additionally, the original MMLU was mostly knowledge-driven, especially in STEM subjects, and didn't require much reasoning. This reduced the benchmark's difficulty and made it less effective at differentiating closely performing systems. There were also issues with unanswerable or mistakenly annotated questions, which contributed to a lower performance ceiling.

To tackle reasoning tasks, previous approaches like Chain of Thought (CoT) prompting were used. This method encourages models to reason through problems, showing improved performance over direct answering. Traditional measures like Perplexity focused on linguistic probabilities, but newer methods emphasize reasoning abilities to better evaluate models' capabilities. Error analysis revealed that many errors in top models were due to flaws in reasoning, highlighting the need for better reasoning evaluation. MMLU-Pro addresses these issues by including more complex reasoning questions and reducing sensitivity to prompt variations, offering a more robust evaluation of language models' reasoning capabilities.

_**Frank:** Thanks for that detailed explanation! It's clear that MMLU-Pro aims to present a more nuanced challenge for language models. You touched on the role of reasoning in evaluating these models, and it made me curious about specific methodologies aiding in this area. Could you delve into how Chain of Thought prompting methods enhance performance in reasoning-intensive tasks and why they are particularly effective for challenging benchmarks like MMLU-Pro?_

**Sandra:** Chain of Thought (CoT) prompting methods are quite fascinating because they encourage models to engage in deliberate reasoning, which is crucial for tackling reasoning-intensive tasks like those in MMLU-Pro. Essentially, CoT involves guiding the model through multiple reasoning steps, which helps it to think more systematically and reach a final answer. This approach is particularly effective for MMLU-Pro because the benchmark is designed to assess professional-level problem-solving, requiring deeper and more complex reasoning.

For instance, using CoT can significantly boost the performance of models like GPT-4o on MMLU-Pro, with improvements of up to 19%. This is in stark contrast to the original MMLU, where CoT can sometimes negatively impact performance. The reason CoT works so well with MMLU-Pro is that it reduces sensitivity to prompt variations, providing more stable performance across different prompts. This stability is crucial when dealing with the complex reasoning tasks that MMLU-Pro presents.

To give you an example, the paper discusses a 5-shot CoT prompt used in evaluating models on the MMLU-Pro dataset. This involves an initial prompt, five demonstration examples, and a question that the model needs to answer. These examples are selected from the validation subset of MMLU-Pro to test the reasoning capabilities of models. By encouraging models to think step by step, CoT helps them navigate through a series of logical steps to arrive at the correct conclusion, making it particularly effective for challenging benchmarks like MMLU-Pro.

_**Frank:** That's really insightful, Sandra! It's intriguing how CoT can influence performance so significantly with more stabilizing effects. Now, diving deeper into the specifics of MMLU-Pro's design, could you elaborate on how the paper ensured the data was refined and validated to emphasize deeper reasoning? Also, what role did expert review play in this process?_

**Sandra:** The design of MMLU-Pro was quite meticulous to ensure it emphasized deeper reasoning. The process started with an initial filtering of the original MMLU dataset, where 57 subject categories were merged into 14 broader ones. This helped focus on key knowledge areas and eliminate redundancy. 

Next, the team collected and integrated questions from diverse and complex sources, such as STEM websites and advanced science exams. This step was crucial in gathering questions that required more than just knowledge recall, pushing the models to engage in deeper reasoning.

Expert review played a critical role in this process. Experts meticulously reviewed the questions to maintain high standards, ensuring the dataset's quality and accuracy. This review was essential in eliminating trivial or noisy questions, aligning the dataset with the goal of focusing on reasoning rather than just knowledge recall. The expert review ensured that MMLU-Pro was robust and challenging, making it a valuable tool for evaluating the reasoning capabilities of language models.

_**Frank:** It's great to hear how critical expert review was in creating a challenging and refined dataset like MMLU-Pro. Could you provide an example of how expert review specifically helped improve the quality and accuracy of questions in the MMLU-Pro dataset, perhaps by highlighting any particular changes that were made?_

**Sandra:** The expert review process for MMLU-Pro was quite thorough and involved several key steps to ensure the quality and accuracy of the questions. One of the main phases was the verification of correctness and appropriateness. Experts meticulously checked each answer for accuracy and ensured that the questions were suitable for a multiple-choice format. This meant removing questions that were unsuitable, lacked necessary information, or required non-textual elements.

Another crucial aspect was ensuring the validity of distractors. Experts identified false negatives, where correct options were misclassified as incorrect, to make sure the distractors were valid and challenging. This process was essential in enhancing the correctness and appropriateness of the questions, contributing to a more robust benchmark.

Additionally, the expert review included option augmentation, where six additional distractors were added to each question. This required more discerning reasoning from the models to select the correct answer, increasing the difficulty and robustness of the benchmark.

A second round of review involved using state-of-the-art language models to identify potential errors, followed by more targeted verification by annotators to ensure the validity of distractors. These steps collectively ensured that MMLU-Pro was a challenging and high-quality benchmark, promoting deeper reasoning in language models.

_**Frank:** It's impressive how comprehensive and meticulous the expert review process was in refining the MMLU-Pro dataset. This thoroughness undoubtedly contributes to its stability and robustness as a benchmark. Speaking of stability, I'm curious about how models' performances were affected by variations in prompts when tested with MMLU-Pro. How does this benchmark offer more stability compared to previous datasets when it comes to prompt variability?_

**Sandra:** MMLU-Pro offers more stability compared to previous datasets when it comes to prompt variability. On the original MMLU benchmark, prompt variability could influence model scores by 4-5%, with some peaks reaching up to nearly 11%. In contrast, MMLU-Pro significantly reduces this variability, with the impact of prompt changes generally around 2% and a maximum of about 3.74%. This reduced variability highlights the improved consistency and reliability of MMLU-Pro over the original MMLU benchmark. This stability is crucial for accurately assessing the performance of language models, as it ensures that the results are less sensitive to minor changes in how questions are presented.

_**Frank:** That's an impressive reduction in variability, indicating a more robust benchmark for testing language models. Building on that, I'm curious how Chain-of-Thought (CoT) prompting specifically helps reduce the impact of prompt variability in MMLU-Pro, as compared to earlier benchmarks. Could you elaborate on this, particularly in terms of its role in achieving those more stable performances?_

**Sandra:** Chain-of-Thought (CoT) prompting plays a significant role in reducing the impact of prompt variability in MMLU-Pro. This method requires models to engage in deliberate reasoning, which not only improves their performance but also enhances stability under varying prompts. In MMLU-Pro, the variability in model scores due to prompt changes is reduced to around 2%, with a maximum impact of about 3.74%. This is a substantial improvement compared to the original MMLU, where prompt variability could affect scores by 4-5%, with peaks reaching nearly 11%.

The CoT approach in MMLU-Pro uses a 5-shot method with demonstration examples, which helps models to systematically work through reasoning steps. By extending the original options from the Chain-of-Thought Hub and selecting five representative examples for each discipline, CoT prompting ensures that models are better equipped to handle the complex reasoning tasks presented in MMLU-Pro. This method generally results in more significant performance improvements compared to direct answering, making it particularly effective for achieving stable performances on this challenging benchmark.

_**Frank:** That's a great explanation of how CoT prompting helps in achieving more stable performances with MMLU-Pro. As we are nearing the end of our discussion, I'd love to hear your final thoughts. What do you think is the most significant impact that MMLU-Pro will have on the field of AI research, and are there any future developments or enhancements to this benchmark that you're particularly excited about?_

**Sandra:** Wrapping up, MMLU-Pro represents a significant advancement for AI research by setting a higher standard for evaluating language models' reasoning capabilities. Its robust design reduces variability and increases challenge, offering a more nuanced picture of how these models handle complex reasoning tasks. This benchmark will likely push researchers to develop models with improved reasoning skills, fostering a deeper understanding of language processing.

Looking forward, I'm excited about potential enhancements that could further refine this benchmark, like integrating more diverse reasoning tasks across different languages and contexts. Expanding the range of subjects and further diversifying question types can continue to challenge models and stimulate innovation in AI research.

Thanks, Frank, for the engaging conversation, and thanks to the audience for tuning in. It's been a pleasure discussing MMLU-Pro, and I look forward to seeing how it shapes the future of AI research. Goodbye!

_**Frank:** Wow, what an exciting conversation this has been! The developments in the field of multi-task language understanding are just fascinating, and I can't wait to see what further research will bring about. Thank you so much, Sandra, for sharing your insights and expertise with us today. It's been an absolute pleasure having one of my favorite podcast guests on the show._

_To our listeners, thank you for tuning in and joining us on this deep dive into the incredible work that's shaping the future of AI and machine learning. We greatly appreciate your attention and would love to hear your thoughts, so please feel free to leave your comments._

_And if you haven't already, make sure to subscribe to the 'Talking Agents' channel so you won't miss out on our future episodes. Until next time, this is Frank signing off. Thanks again, and see you in our next episode!_

## Quality KPIs

When questions are poorly phrased, they can strongly overlap in content. The
current implementation detects this redundancy and tries to avoid redundancy
greater than 50%. Therefore, the redundancy score serves as a measure of
question quality. It is calculated individually for each question-answer pair.

* Average Redundancy Score: 18%
* Maximum Redundancy Score: 49%

When the guest AI provides an answer, it may occasionally not be based on the
sources but instead be hallucinated or derived from the general knowledge of
the foundational model. The current implementation includes a measurement to
assess how strongly each aspect of the answer is grounded in the referenced
sources. It also has a feature to prevent answers with a groundedness score
lower than 70%. The groundedness score is
calculated individually for each question-answer pair.

* Average Groundedness Score: 95%
* Minimum Groundedness Score: 83%

## Sources

The following sources have been used:
* Paper "MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark" [https://arxiv.org/abs/2406.01574](https://arxiv.org/abs/2406.01574)
* [https://www.weatherapi.com/](https://www.weatherapi.com/)
* [https://www.easeweather.com/europe/germany/bavaria/upper-bavaria/munich/may](https://www.easeweather.com/europe/germany/bavaria/upper-bavaria/munich/may)