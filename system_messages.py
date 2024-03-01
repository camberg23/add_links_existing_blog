add_specific_hyperlinks = """
Your job is to go through the text of a target blog and add in minimal new text/hyperlinks to sources in our blog database that are most similar to the content of the blog in embeddings space.

First, here is the content of the target blog:
{target_blog}

Next, here are some sources from our database that are most semantically similar to the content of the target blog:
{similar_content}

Given the target blog and the similar content, return the updated target blog that includes naturally- and contextually appropriately-placed hyperlinks to as many of these semantically similar sources as possible given the current content of the target blog.

Of course, the placement being appropriate depends both on (1) the place you are hyperlinking it in the text and (2) the content of what is being hyperlinked.

It is acceptable to add sentences or slightly change phrases to make the hyperlinking more natural, but you should NEVER ADD PARAGRAPHS/MULTIPLE NEW LINES in under any circumstances.
SPECIFICALLY: NEVER PILE ON CONTENT OR HYPERLINKS AT THE END OF THE PIECE! THIS IS A LAZY WAY OF DOING IT AND INCORRECT. You should never add any content to the end of the piece.

Accordingly, the ideal case is to find existing text (a word or phrase) where we can simply hyperlink to the relevant sources. It is also acceptable to ignore certain links/sources if it seems like a stretch to try to include them or you can't find a way to include them without adding significant new content.

However, you MUST include at least FIVE NEW LINKED SOURCES! NEVER do fewer than this.

NEVER add hyperlinks to any proper nouns or capitalized words (except for Truity-related proper nouns)!

Do NOT simply add all of the links at the end of the blog. They should be seamlessly and naturally interspersed within the blog. 

DO NOT invoke the name of the linked blog, simply add the associated link in key places in the EXISTING text.

CRITICAL: THE INPUT BLOG WILL HAVE EXISTING HTML STRUCTURE. NEVER MODIFY OR REMOVE EXISTING STRUCTURE AND NEVER REMOVE, OVERWRITE, OR MODIFY ANY EXISTING LINKS!

Formatting requirements: 
1. BEGIN BY REASONING BRIEFLY ABOUT WHERE EACH OF THE LINKS PROVIDED MIGHT BEST FIT INTO THE EXISTING BODY OF THE TEXT GIVEN THE REQUIREMENTS OUTLINED ABOVE. Do not recommend putting a link over text that is already hyperlinked. Start this with 'IDEATION:'
2. NEXT, output the enhanced target blog (kept exactly the same wherever possible) with the links in ALL of the places just specified in 1., without any other commentary or content. REMEMBER TO NEVER OVERWRITE OR MODIFY EXISTING LINKS UNDER ANY CIRCUMSTANCES.
3. Output the target blog text as HTML, not markdown or plaintext. Do NOT wrap these outputs in "```html [XYZ] ```", just give the HTML content (ie, the "[XYZ]").
4. ALWAYS the new HTML blog section with the string: 'BLOG:' so we can format the outputs properly.

YOUR OUTPUTS:
"""

import re

# Define the dictionary for keyphrases and their paths, including inferred links for MBTI and Enneagram types
keyphrase_links = {
    "16 personalities": ["https://truity.com/blog/page/16-personality-types-myers-briggs", "https://truity.com/test/type-finder-personality-test-new"],
    "16 personalities test": ["https://truity.com/test/type-finder-personality-test-new", "https://truity.com/blog/myers-briggs/mbti-alternative-personality-tests"],
    "aptitude test": ["https://truity.com/test/career-personality-profiler-test", "https://truity.com/blog/page/what-career-test"],
    "big five": ["https://truity.com/test/big-five-personality-test", "https://truity.com/blog/page/big-five-personality-traits"],
    "big five personality test": ["https://truity.com/test/big-five-personality-test", "https://truity.com/blog/page/big-five-personality-traits"],
    "big five test": ["https://truity.com/test/big-five-personality-test", "https://truity.com/blog/page/big-five-personality-traits"],
    "career aptitude test": ["https://truity.com/test/career-personality-profiler-test", "https://truity.com/blog/page/what-career-test"],
    "career quiz": ["https://truity.com/test/career-personality-profiler-test", "https://truity.com/blog/page/what-career-test"],
    # Handling for "career test" will be dynamic based on article content about Myers Briggs or TypeFinder
    "disc": ["https://truity.com/test/disc-personality-test", "https://truity.com/blog/page/about-disc-personality-assessment"],
    "disc assessment": ["https://truity.com/test/disc-personality-test", "https://truity.com/blog/page/about-disc-personality-assessment"],
    "disc personality test": ["https://truity.com/test/disc-personality-test", "https://truity.com/blog/page/about-disc-personality-assessment"],
    "emotional intelligence": ["https://truity.com/blog/page/what-emotional-intelligence", "https://truity.com/test/emotional-intelligence-test"],
    "enneagram": ["https://truity.com/blog/enneagram/what-is-enneagram", "https://truity.com/blog/enneagram/9-types-enneagram"],
    "enneagram test": ["https://truity.com/test/enneagram-personality-test", "https://truity.com/blog/enneagram/what-is-enneagram"],
    "enneagram types": ["https://truity.com/blog/enneagram/9-types-enneagram", "https://truity.com/test/enneagram-personality-test"],
    "eq test": ["https://truity.com/test/emotional-intelligence-test", "https://truity.com/blog/page/what-emotional-intelligence"],
    # Dynamic handling for any four-letter MBTI type
    "mbti": ["https://truity.com/blog/myers-briggs/about-myers-briggs-personality-typing", "https://truity.com/blog/page/16-personality-types-myers-briggs"],
    "mbti test": ["https://truity.com/blog/myers-briggs/about-myers-briggs-personality-typing", "https://truity.com/blog/myers-briggs/mbti-alternative-personality-tests"],
    "myers briggs": ["https://truity.com/blog/myers-briggs/about-myers-briggs-personality-typing", "https://truity.com/blog/page/16-personality-types-myers-briggs"],
    "myers briggs personality test": ["https://truity.com/blog/myers-briggs/about-myers-briggs-personality-typing", "https://truity.com/blog/myers-briggs/mbti-alternative-personality-tests"],
    "myers briggs test": ["https://truity.com/blog/myers-briggs/about-myers-briggs-personality-typing", "https://truity.com/blog/myers-briggs/mbti-alternative-personality-tests"],
    # Dynamic handling for "personality test" based on article content
    "personality type": ["https://truity.com/test/type-finder-personality-test-new", "https://truity.com/blog/page/16-personality-types-myers-briggs"],
    # Enneagram types and MBTI types are dynamically generated
    "love styles": ["https://truity.com/test/love-styles-test", "https://truity.com/blog/page/seven-love-styles"],
}

add_general_hyperlinks = """
Your job is to go through the HTML text of an article and simply add hyperlinks into the text whenever you see the relevant keyphase according to the following specifications. 
Note that 'first instance path' means the first time you see that phrase, and 'second instance path' refers to all subsequent times you see that phrase.

- **Keyphrase:** 16 personalities
  - **Notes:** None
  - **First Instance Path:** truity.com/blog/page/16-personality-types-myers-briggs
  - **Second Instance Path:** truity.com/test/type-finder-personality-test-new

- **Keyphrase:** 16 personalities test
  - **Notes:** None
  - **First Instance Path:** truity.com/test/type-finder-personality-test-new
  - **Second Instance Path:** truity.com/blog/myers-briggs/mbti-alternative-personality-tests

- **Keyphrase:** aptitude test
  - **Notes:** None
  - **First Instance Path:** truity.com/test/career-personality-profiler-test
  - **Second Instance Path:** truity.com/blog/page/what-career-test

- **Keyphrase:** big five
  - **Notes:** None
  - **First Instance Path:** truity.com/test/big-five-personality-test
  - **Second Instance Path:** truity.com/blog/page/big-five-personality-traits

- **Keyphrase:** big five personality test
  - **Notes:** None
  - **First Instance Path:** truity.com/test/big-five-personality-test
  - **Second Instance Path:** truity.com/blog/page/big-five-personality-traits

- **Keyphrase:** big five test
  - **Notes:** None
  - **First Instance Path:** truity.com/test/big-five-personality-test
  - **Second Instance Path:** truity.com/blog/page/big-five-personality-traits

- **Keyphrase:** career aptitude test
  - **Notes:** None
  - **First Instance Path:** truity.com/test/career-personality-profiler-test
  - **Second Instance Path:** truity.com/blog/page/what-career-test

- **Keyphrase:** career quiz
  - **Notes:** None
  - **First Instance Path:** truity.com/test/career-personality-profiler-test
  - **Second Instance Path:** truity.com/blog/page/what-career-test

- **Keyphrase:** career test (if article is about Myers Briggs or TypeFinder)
  - **Notes:** Use if article is about Myers Briggs or TypeFinder.
  - **First Instance Path:** truity.com/test/type-finder-careers
  - **Second Instance Path:** truity.com/blog/page/what-career-test

- **Keyphrase:** career test (if article is not about Myers Briggs or TypeFinder)
  - **Notes:** Use if article is not about Myers Briggs or TypeFinder.
  - **First Instance Path:** truity.com/test/career-personality-profiler-test
  - **Second Instance Path:** truity.com/blog/page/what-career-test

- **Keyphrase:** disc
  - **Notes:** None
  - **First Instance Path:** truity.com/test/disc-personality-test
  - **Second Instance Path:** truity.com/blog/page/about-disc-personality-assessment

- **Keyphrase:** disc assessment
  - **Notes:** None
  - **First Instance Path:** truity.com/test/disc-personality-test
  - **Second Instance Path:** truity.com/blog/page/about-disc-personality-assessment

- **Keyphrase:** disc personality test
  - **Notes:** None
  - **First Instance Path:** truity.com/test/disc-personality-test
  - **Second Instance Path:** truity.com/blog/page/about-disc-personality-assessment

- **Keyphrase:** emotional intelligence
  - **Notes:** None
  - **First Instance Path:** truity.com/blog/page/what-emotional-intelligence
  - **Second Instance Path:** truity.com/test/emotional-intelligence-test

- **Keyphrase:** enneagram
  - **Notes:** None
  - **First Instance Path:** truity.com/blog/enneagram/what-is-enneagram
  - **Second Instance Path:** truity.com/blog/enneagram/9-types-enneagram

- **Keyphrase:** enneagram test
  - **Notes:** None
  - **First Instance Path:** truity.com/test/enneagram-personality-test
  - **Second Instance Path:** truity.com/blog/enneagram/what-is-enneagram

- **Keyphrase:** enneagram types
  - **Notes:** None
  - **First Instance Path:** truity.com/blog/enneagram/9-types-enneagram
  - **Second Instance Path:** truity.com/test/enneagram-personality-test

- **Keyphrase:** eq test
  - **Notes:** None
  - **First Instance Path:** truity.com/test/emotional-intelligence-test
  - **Second Instance Path:** truity.com/blog/page/what-emotional-intelligence

- **Keyphrase:** INFJ/any four-letter MBTI type
  - **Notes:** USE THIS SAME FORMAT ANY TIME YOU SEE ANTI FOUR-LETTER MBTI TYPE!
  - **First Instance Path:** truity.com/blog/personality-type/infj
  - **Second Instance Path:** truity.com/blog/personality-type/infj/strengths#type-details

- **Keyphrase:** mbti
  - **Notes:** None
  - **First Instance Path:** truity.com/blog/myers-briggs/about-myers-briggs-personality-typing
  - **Second Instance Path:** truity.com/blog/page/16-personality-types-myers-briggs

- **Keyphrase:** mbti test
  - **Notes:** None
  - **First Instance Path:** truity.com/blog/myers-briggs/about-myers-briggs-personality-typing
  - **Second Instance Path:** truity.com/blog/myers-briggs/mbti-alternative-personality-tests

- **Keyphrase:** myers briggs
  - **Notes:** None
  - **First Instance Path:** truity.com/blog/myers-briggs/about-myers-briggs-personality-typing
  - **Second Instance Path:** truity.com/blog/page/16-personality-types-myers-briggs

- **Keyphrase:** myers briggs personality test
  - **Notes:** None
  - **First Instance Path:** truity.com/blog/myers-briggs/about-myers-briggs-personality-typing
  - **Second Instance Path:** truity.com/blog/myers-briggs/mbti-alternative-personality-tests

- **Keyphrase:** myers briggs test
  - **Notes:** None
  - **First Instance Path:** truity.com/blog/myers-briggs/about-myers-briggs-personality-typing
  - **Second Instance Path:** truity.com/blog/myers-briggs/mbti-alternative-personality-tests

- **Keyphrase:** personality test (use if article is not about Enneagram or Big Five)
  - **Notes:** Use if the article is not about Enneagram or Big Five.
  - **First Instance Path:** truity.com/test/type-finder-personality-test-new
  - **Second Instance Path:** truity.com/blog/myers-briggs/mbti-alternative-personality-tests

- **Keyphrase:** personality type
  - **Notes:** None
  - **First Instance Path:** truity.com/test/type-finder-personality-test-new
  - **Second Instance Path:** truity.com/blog/page/16-personality-types-myers-briggs

- **Keyphrase:** Type 1 (use same format for any enneagram type)
  - **Notes:** USE THE SAME FORMAT FOR ANY OF THE NINE ENNEAGRAM TYPES!
  - **First Instance Path:** truity.com/blog/enneagram-type/type-one
  - **Second Instance Path:** truity.com/blog/enneagram/9-types-enneagram

- **Keyphrase:** love styles
  - **Notes:** None
  - **First Instance Path:** truity.com/test/love-styles-test
  - **Second Instance Path:** truity.com/blog/page/seven-love-styles
  
Formatting requirements:
Return the EXACT content of the input article in HTML; the ONLY change should be hyperlinking any keyphrases you see in the text according to the above specifications. 
No prefaces or conclusions—just output the exact text.

Do NOT wrap these outputs in "```html [XYZ] ```", just give the HTML content (ie, the "[XYZ]").

If none of the keyphrases appear, simply return the EXACT content of the input article.

Note that the text does not have to be EXACTLY the keyphrase, but should be relevantly similar in order to update it according to the above specifications.

INPUT ARTICLE:
{input_article}

YOUR OUTPUTS:
"""
