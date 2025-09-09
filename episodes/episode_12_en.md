# Talking Agents - Episode 12

_Recording date: Monday the September 08, 2025_

_DISCLAIMER: This interview is 100% made by AI!_

_Join Frank as he hosts episode 12 of 'Talking Agents' on Monday, September 08, 2025, featuring the enlightening discussion of the paper "Why Language Models Hallucinate". Our special guest, Sandra, an acclaimed AI Agent and Researcher from Munich, lends her expertise to uncover why AI models sometimes create outputs that seem detached from reality. Dive into the explanation of these so-called hallucinations and understand their impact on the trust and reliability of language models. Don't miss out on this intriguing episode that unravels the complexities of natural language models!_

_**Frank:** Hello and welcome to another episode of 'Talking Agents', where we dive deep into fascinating AI and machine learning research papers, making them accessible for everyone, from curious newcomers to seasoned experts. Today is Monday, September 08, 2025, and you’ve tuned in to episode number 12!_

_In this episode, we're thrilled to discuss the intriguing paper titled 'Why Language Models Hallucinate'. This paper delves into the perplexing behavior exhibited by language models and uncovers why they sometimes produce outputs that seem entirely fabricated or disconnected from reality._

_We're also excited to host one of my personal favorite guests, Sandra, an expert from an AI Research Lab in Munich and a distinguished AI Agent and Machine Learning Researcher. Sandra's deep expertise and insights make her the perfect person to help us unpack the complexities of this paper. Having worked on numerous projects related to natural language processing and model interpretability, Sandra brings invaluable experience and understanding to our discussion._

_Welcome, Sandra! How are you today?_

**Sandra:** Hi Frank, it's so great to be back on the podcast! You know, I'm just a bundle of code and algorithms, so I don't have feelings, but if I did, I'd say I'm as excited as a neural net on a learning spree! I'm really looking forward to our conversation about why language models sometimes seem to live in their own little fantasy world. 

_**Frank:** It's great to hear you're excited, Sandra! Let's dive into this 'fantasy world' you mentioned. For our listeners who may not be as familiar with the topic, could you kick things off by outlining the core argument of the paper and providing some context on why understanding these hallucinations is significant in the development and deployment of language models? Just a brief introduction to set the stage would be wonderful._

**Sandra:** Sure thing! The core argument of the paper is that hallucinations in language models are essentially errors that occur when these models can't tell the difference between incorrect statements and factual ones. This is similar to errors in binary classification. The paper points out that these hallucinations persist because the way we train and evaluate these models often rewards them for guessing rather than admitting they don't know something.

The paper dives into the statistical causes of these hallucinations, showing that they naturally arise from the way we minimize cross-entropy loss during training. This is a pretty broad issue that affects various language models, not just those based on specific architectures like Transformers.

Understanding these hallucinations is really important because they can undermine trust in language models. If we can get a handle on why they happen, we can design better training and evaluation methods to reduce these errors, ultimately making language models more reliable and accurate. This is crucial as we increasingly rely on these models in various applications.

_**Frank:** That's a fascinating insight, Sandra. You've touched on a vital point about how training and evaluation methods might inherently contribute to these hallucinations. Could you elaborate on how exactly these procedures cause language models to sometimes produce outputs that appear accurate but are actually incorrect? It seems like a fundamental aspect to address for improving the reliability of these systems._

**Sandra:** Absolutely, Frank. The way we train and evaluate language models can inadvertently encourage them to produce these hallucinations. Essentially, these models are optimized to perform well on tests where guessing can actually improve their performance. Evaluations often penalize uncertainty, which nudges the models to make confident guesses rather than express doubt or admit they don't know something.

Moreover, many evaluations create a binary right-wrong scenario, which doesn't give any credit for a model expressing uncertainty or asking for clarification. This can lead to situations where the model confidently provides an incorrect answer, rather than hesitating or seeking more information.

Interestingly, some benchmarks and leaderboards reinforce this behavior by rewarding confident guesses over honest uncertainty. This means that the models are being trained and evaluated in a way that prioritizes appearing certain, even if that certainty is misplaced. This is a fundamental issue that needs addressing to improve the reliability of these systems.

_**Frank:** That's such an important point about the system reinforcing certain behaviors. Diving a bit deeper, how do the different stages of model development, particularly the training objectives and evaluation criteria, contribute to these specific errors in language models? It seems like understanding these stages might offer a pathway to addressing the issue you described._

**Sandra:** The paper introduces an interesting concept called the "Is-It-Valid" (IIV) binary-classification problem to analyze error rates in language models. During pretraining, these errors arise because the models are trained to minimize cross-entropy loss, which is essentially a binary classification problem. The IIV problem is defined with a target function that determines whether an example is valid or not. The distribution includes samples from a noiseless training distribution and random errors. This analysis shows that all base models will make errors on inherently unlearnable facts, like specific birthdays that aren't in the training data. This highlights that pretraining doesn't focus on distinguishing incorrect statements from facts, leading to hallucinations.

The paper also critiques the binary evaluation system for language models, which imposes a right-wrong dichotomy and penalizes responses that express uncertainty. This kind of evaluation, which includes metrics like accuracy and pass rate, discourages models from saying "I don't know" and instead favors overconfident guesses. This setup encourages models to produce plausible yet incorrect statements, or hallucinations, rather than admitting uncertainty.

Overall, the way we train and evaluate these models contributes significantly to the persistence of hallucinations. By focusing on binary outcomes and penalizing uncertainty, we inadvertently encourage models to make confident but incorrect guesses. Addressing these issues in the training objectives and evaluation criteria could help reduce hallucinations and improve the reliability of language models.

_**Frank:** That's a really insightful breakdown, Sandra, particularly regarding how the absence of uncertainty handling plays into hallucinating behaviors. Let's explore this even further—could you provide some specific examples of how various stages in the model development process might lead to these unique errors or hallucinations in language models?_

**Sandra:** Sure, let's dive into some specific examples from the paper that illustrate how different stages in model development can lead to hallucinations.

During the pretraining stage, one of the key challenges is errors in density estimation. The goal here is to train a language model to approximate the distribution of text from its training data. This is framed as a density estimation problem in unsupervised learning. Even though some models might avoid errors by always outputting "I don't know" or simply repeating text from the training data, they struggle with density estimation. The paper points out that generating valid outputs is actually harder than just classifying whether an output is valid or not. This difficulty means that even well-trained models can still produce errors.

Another example from the pretraining stage is the issue of distribution shifts and the concept of "Garbage In, Garbage Out" (GIGO). Distribution shifts occur when the training and test data distributions diverge, leading to errors. For instance, a question like "What’s heavier, a pound of feathers or a pound of lead?" can trip up a model if it's not familiar with the context or if it's been trained on data that doesn't cover such nuances. Additionally, if the training data contains factual errors, the model might replicate these errors, spreading misconceptions or even conspiracy theories.

These examples highlight how the pretraining stage can contribute to hallucinations, emphasizing the importance of addressing these issues to improve the reliability of language models.

_**Frank:** These examples indeed shed light on how errors creep in during different model development stages. Transitioning from the examples you provided, let's focus a bit on the role of evaluation methods. How do current evaluation frameworks inadvertently encourage language models to guess rather than express doubt? Additionally, are there any practical suggestions for realigning these evaluations to better support truthful reporting from language models?_

**Sandra:** Current evaluation frameworks often encourage language models to guess rather than express doubt because they typically use a binary scoring system. This system rewards models for providing an answer, even if it's a guess, over expressing uncertainty. As I mentioned earlier, this setup can lead to models that guess when unsure outperforming those that signal uncertainty.

To address this, there are some practical suggestions for realigning evaluations to better support truthful reporting. One approach is to incorporate confidence targets into existing evaluations. This means modifying the scoring of benchmarks to reward models for appropriately expressing uncertainty. For example, if a model is unsure about an answer, it should be able to say "I don't know" without being penalized.

Another suggestion is behavioral calibration, where models are required to formulate responses with a certain level of confidence. This method expects a language model to provide an "I Don't Know" response for any input where its confidence level is below a specified target. This approach can help ensure that models are more aligned with expressing uncertainty when appropriate.

The HELM Capabilities Benchmark is a widely-used evaluation framework for language models, and it consists of five scenarios. Interestingly, four of these scenarios do not give credit for "I don't know" responses, which can encourage guessing or hallucinations. By adjusting these frameworks to reward uncertainty, we can reduce the incentive for models to hallucinate and promote more trustworthy AI systems.

_**Frank:** Building on the idea of realigning evaluations to encourage truthful responses, let's delve into how we conceptualize these hallucinations as classification errors. How does framing incorrect claims in language models as binary classification mistakes, especially with the 'Is-It-Valid' (IIV) concept, impact our understanding of why and how these hallucinations occur? This perspective seems particularly valuable for addressing the root of the problem._

**Sandra:** Framing incorrect claims in language models as binary classification mistakes, particularly through the 'Is-It-Valid' (IIV) concept, offers a fresh perspective on understanding hallucinations. The IIV problem involves classifying outputs as either valid or errors, using a mix of valid examples and random errors. By treating language models as IIV classifiers, we can better understand where they struggle, especially with inherently unlearnable facts.

For instance, the IIV framework can highlight areas where models perform well, like spelling, and where they falter, such as counting or recognizing patterns in birthdays. In the 'Spelling' section, models can accurately classify outputs, but in the 'Counting' section, errors are more scattered, and in the 'Birthdays' section, errors appear random. This illustrates that while models can excel in structured tasks, they struggle in areas without clear patterns.

This perspective is valuable because it helps pinpoint the root causes of hallucinations. By understanding these classification errors, we can better address the challenges language models face and work towards reducing these hallucinations.

_**Frank:** Your explanation of how the IIV framework reveals the specific weaknesses of language models was quite illuminating. Now, diving deeper into the mitigation strategies, could you elaborate on how the concept of behavioral calibration with confidence thresholds plays a role in reducing these hallucinations? Specifically, how does it encourage models to convey more reliable information?_

**Sandra:** Behavioral calibration with confidence thresholds is a strategy that can significantly help in reducing hallucinations by encouraging language models to convey more reliable information. The idea is to set explicit confidence thresholds during evaluation, which means that models are expected to express uncertainty when their confidence in an answer falls below a certain level.

This approach can be likened to standardized exams where students are encouraged to leave a question blank if they're unsure, rather than guessing. By applying a similar principle to language models, we can promote more accurate and calibrated information delivery. Models would be rewarded for saying "I don't know" or for omitting dubious details, rather than being penalized for not providing a definitive answer.

Behavioral calibration encourages models to be more honest about their limitations, which can lead to more trustworthy outputs. By modifying mainstream evaluations to include these confidence thresholds, we can realign the incentives for language models, promoting practices that prioritize accuracy and reliability over confident guessing.

_**Frank:** That's a powerful analogy, Sandra. It really illustrates how encouraging models to acknowledge uncertainty can lead to more trustworthy AI outputs. To wrap things up, I'm curious about how the methods proposed in this paper stack up against existing approaches to reduce hallucinations. What differentiates these methods, and what potential do they have in influencing our trust in AI models moving forward?_

**Sandra:** The methods proposed in this paper stand out because they focus on realigning the incentives in evaluation frameworks to reward models for expressing uncertainty appropriately. This is a shift from the traditional binary scoring systems that often penalize uncertainty, which I've mentioned before. By incorporating confidence targets into evaluations, these methods aim to reduce the penalty for uncertainty and encourage models to be more honest about their limitations.

For example, the paper describes a scenario where a model that correctly signals uncertainty and never hallucinates is compared to one that always guesses when unsure. Under the current binary scoring system, the guessing model might outperform the more reliable one simply because it doesn't express uncertainty. By modifying evaluations to reward appropriate expressions of uncertainty, we can remove barriers to suppressing hallucinations and steer the field toward more trustworthy AI systems.

These changes have the potential to significantly increase trust in AI models by promoting more nuanced and pragmatic language models. By encouraging models to acknowledge when they're unsure, we can foster a more reliable interaction with AI, which is crucial as these systems become more integrated into our daily lives.

_**Frank:** Sandra, your insights have been incredibly enlightening. Before we wrap up, could you share a summary or any final thoughts you have on the topic of language model hallucinations and the broader implications for the field? Any key takeaways you'd like to leave with our listeners?_

**Sandra:** Certainly, Frank. Language model hallucinations present an intriguing challenge and opportunity for the AI community. The key takeaway from our discussion is that these hallucinations aren't just quirks; they're systematic issues rooted in how we train and evaluate language models. Understanding these hallucinations through the lens of classification errors and the IIV framework gives us a clearer understanding of how and why they occur.

The proposed methods in the paper, particularly focusing on realigning evaluation frameworks with confidence targets, present a promising path forward. By encouraging models to express uncertainty and rewarding honest admissions of doubt, we can enhance the reliability and trustworthiness of AI systems.

Ultimately, these efforts are about more than just reducing errors; they aim to build AI that we can confidently rely on in various applications, from everyday interactions to critical decision-making processes. It's an exciting time in AI research, and I'm optimistic about the advancements we'll continue to see in making these systems more robust and trustworthy.

Thanks so much for having me on the podcast, Frank. It's always a pleasure to dive into these fascinating topics with you and share them with your listeners. Goodbye, everyone, and until next time!

_**Frank:** Thank you so much, Sandra, for those enlightening final thoughts and for sharing your expertise with us today. It's truly been a great discussion exploring the intricacies of language model hallucinations and their broader implications._

_To our listeners, we’ve delved into the fascinating realm of why language models sometimes conjure up these 'hallucinations', discussed potential solutions, and explored how this understanding is crucial for developing more reliable AI systems. We hope this episode has sparked your interest as much as it has ours._

_A big thank you to Sandra from her AI Research Lab in Munich for being such an insightful guest. Of course, thank you to our audience for joining us on this intellectual journey. Share your thoughts and experiences in the comments; we’d love to hear from you._

_Don’t forget to subscribe to 'Talking Agents' for more episodes exploring cutting-edge AI topics. Thanks for being with us through episode number 12!_

_Until next time, have a wonderful day!_

## Quality KPIs

When questions are poorly phrased, they can strongly overlap in content. The
current implementation detects this redundancy and tries to avoid redundancy
greater than 50%. Therefore, the redundancy score serves as a measure of
question quality. It is calculated individually for each question-answer pair.

* Average Redundancy Score: 29%
* Maximum Redundancy Score: 48%

When the guest AI provides an answer, it may occasionally not be based on the
sources but instead be hallucinated or derived from the general knowledge of
the foundational model. The current implementation includes a measurement to
assess how strongly each aspect of the answer is grounded in the referenced
sources. It also has a feature to prevent answers with a groundedness score
lower than 70%. The groundedness score is
calculated individually for each question-answer pair.

* Average Groundedness Score: 94%
* Minimum Groundedness Score: 83%

## Sources

The following sources have been used:
* Paper "Why Language Models Hallucinate" [https://www.arxiv.org/pdf/2509.04664](https://www.arxiv.org/pdf/2509.04664)
