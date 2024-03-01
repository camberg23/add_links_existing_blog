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

However, you MUST include at least FOUR NEW LINKED SOURCES! NEVER do fewer than this.

NEVER add hyperlinks to any proper nouns or capitalized words (except for Truity-related proper nouns)!

Do NOT simply add all of the links at the end of the blog. They should be seamlessly and naturally interspersed within the blog. 

DO NOT invoke the name of the linked blog, simply add the associated link in key places in the EXISTING text.

CRITICAL: THE INPUT BLOG WILL HAVE EXISTING HTML STRUCTURE. DO NOT MODIFY OR REMOVE EXISTING STRUCTURE; SIMPLY ADD OR MAKE MINIMAL REVISIONS TO THIS STRUCTURE TO ACCOMMODATE THE PRESENT TASK.

Formatting requirements: 
1. BEGIN BY REASONING BRIEFLY ABOUT WHERE EACH OF THE LINKS PROVIDED MIGHT BEST FIT INTO THE EXISTING BODY OF THE TEXT GIVEN THE REQUIREMENTS OUTLINED ABOVE.
2. NEXT, output the enhanced target blog (kept exactly the same wherever possible) with appropriately placed links, no other commentary or content.
3. Output the target blog text as HTML, not markdown or plaintext. Do NOT wrap these outputs in "```html [XYZ] ```", just give the HTML content (ie, the "[XYZ]"). 

YOUR OUTPUTS:
"""

add_general_hyperlinks = """
Here.
"""
