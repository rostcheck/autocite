# autocite - automatic identification and generation of citations

### Author
David Rostcheck, david@rostcheck.com, informed by work with Lara Schneible M.Ed

Given an academic-style paper, autocite identifies those references and/or claims requiring citations and locates appropriate citations for them

Autocite is a data science experiment that currently does not work. 

The intent was to use an LLM to identify sentences needing citations, then search Google Scholar to identify references with high relevancy and high citation count.

## Theory
Traditional academic workflow starts research with a literature study to understand the state of the field and identify open questions within it. Fast-moving fields such as AI, have developed ecologies of explainers, who summarize and review papers via YouTube videos, newsletters, and other such means. Those operating in such fields may often possess current knowledge of the field but since they obtained this knowledge through the explainer layer, when they write papers they need to go back to identify the current academic papers supporting their work.

## Current issues
The data pipeline has proven troublesome. autocite has a LLM prompt to identify areas needing citation in a text essay, which seems to work, but needs analytical validation. To fine-tune the prompt to give better results, we were extracting text from known popular papers in Machine Learning and stripping the citations to form a data set for identifying true and false positives and negatives. 

Text extraction in particular poses a problem. Autocite can extract text from PDFs but it contains formatting issues like issues with equations and sentence-breaking, especially in multi-column format. We were attempting to use Claude 3 Haiku via AWS Bedrock to clean the text, and it often works, but results are currently inconsistent. Without well-formed text, reference extraction for testing does not work well on many papers.

Another current issue relates to Claude 3 Haiku scaling. Haiku has a long context window of 200,000 tokens (more than enough for any academic paper) but slows down as max_tokens provided increase. Haiku appears to scale inconsistently - scaling geometrically faster than the max_tokens provided rises, but then sometimes giving much faster results at around 32,000 tokens, and sometimes refusing to answer at all or suddenly answering poorly depending on the paper's length. These behaviors may relate to the above data quality issues and need more reproduction and investigation.

Finally, some papers contain voluminous appendices, which do not contribute to the problem; we need to identify how to skip them in text extraction. 

## Strategic Path
Because extracting properly-formatted text from a PDF is inherently a high difficulty cognitive task, we should try operating directly from the PDF. Doing so requires a multimodal LLM, the top contenders as of April 2024 being GPT4-V and the Claude 3 models. Claude 3's vision features are not currently available through the AWS Bedrock API we are using so we would need to call via the Claude API, use GPT4-V, or wait for Bedrock's API to implement vision.  

## Credit:
* The LLM prompt in prompt.txt contains sample lines from Wu, S. T. I., Demetriou, D., & Husain, R. A. (2023, June). Honor Ethics: The Challenge of Globalizing Value Alignment in AI. In Proceedings of the 2023 ACM Conference on Fairness, Accountability, and Transparency (pp. 593-602).
* The papers used for code tuning of PDF-to-text extraction pipeline and for reference identification testing are the topbots.com article [The GenAI Frontier: 10 Transformative LLM Research Papers of 2023 from LLaMA to GPT-4](https://www.topbots.com/top-llm-research-papers-2023/#llama) December 5, 2023 by Mariya Yao. Papers were downloaded in PDF format from arxiv.org.
