prompt_chirp_doc = """
DOCUMENTATION:
Scripting and prompting tips

Creating engaging and natural-sounding audio from text requires understanding the nuances of spoken language and translating them into script form. The following tips will help you craft scripts that sound authentic and capture the chosen tone.
Understanding the goal: Natural speech

The primary objective is to make the synthesized voice sound as close to a natural human speaker as possible. This involves:

    Mimicking Natural Pacing: How quickly or slowly someone speaks.
    Creating Smooth Flow: Ensuring seamless transitions between sentences and phrases.
    Adding Realistic Pauses: Incorporating pauses for emphasis and clarity.
    Capturing Conversational Tone: Making the audio sound like a real conversation.

Key techniques for natural speech

    Punctuation for Pacing and Flow
        Periods (.): Indicate a full stop and a longer pause. Use them to separate complete thoughts and create clear sentence boundaries.
        Commas (,): Signal shorter pauses within sentences. Use them to separate clauses, list items, or introduce brief breaks for breath.
        Ellipses (...): Represent a longer, more deliberate pause. They can indicate trailing thoughts, hesitation, or a dramatic pause.
            Example: "And then... it happened."
        Hyphens (-): Can be used to indicate a brief pause or a sudden break in thought.
            Example: "I wanted to say - but I couldn't."

    Incorporating Pauses and Disfluencies
        Strategic Pauses: Use ellipses, commas, or hyphens to create pauses in places where a human speaker would naturally pause for breath or emphasis.
        Disfluencies (Ums and Uhs): While some Cloud Text-to-Speech models handle disfluencies automatically, understanding their role is crucial. They add authenticity and make the speech sound less robotic. Even if the model adds them, being aware of where they would naturally occur in human speech helps you understand the overall flow of your script.

    Experimentation and Iteration
        Re-synthesizing: Don't be afraid to re-synthesize the same message with the same voice multiple times. Minor tweaks to punctuation, spacing, or word choice can significantly impact the final audio.
        Listen Critically: Pay close attention to the pacing, flow, and overall tone of the synthesized audio. Identify areas that sound unnatural and adjust your script accordingly.
        Voice Variation: If the system allows for it, try using different voices to see which one best suits your script and chosen tone.

    Practical Scripting Tips
        Read Aloud: Before synthesizing, read your script aloud. This will help you identify awkward phrasing, unnatural pauses, and areas that need adjustment.
        Write Conversationally: Use contractions (e.g., "it's," "we're") and informal language to make the script sound more natural.
        Consider the Context: The tone and pacing of your script should match the context of the audio. A formal presentation will require a different approach than a casual conversation.
        Break Down Complex Sentences: Long, convoluted sentences can be difficult for TTS engines to handle. Break them down into shorter, more manageable sentences.

    Sample Script Improvements

        Original Script (Robotic): "The product is now available. We have new features. It is very exciting."

        Improved Script (Natural): "The product is now available... and we've added some exciting new features. It's, well, it's very exciting."

        Original Script (Robotic): "This is an automated confirmation message. Your reservation has been processed. The following details pertain to your upcoming stay. Reservation number is 12345. Guest name registered is Anthony Vasquez Arrival date is March 14th. Departure date is March 16th. Room type is Deluxe Suite. Number of guests is 1 guest. Check-in time is 3 PM. Check-out time is 11 AM. Please note, cancellation policy requires notification 48 hours prior to arrival. Failure to notify within this timeframe will result in a charge of one night's stay. Additional amenities included in your reservation are: complimentary Wi-Fi, access to the fitness center, and complimentary breakfast. For any inquiries, please contact the hotel directly at 855-555-6689 Thank you for choosing our hotel."

        Improved Script (Natural): "Hi Anthony Vasquez! We're so excited to confirm your reservation with us! You're all set for your stay from March 14th to March 16th in our beautiful Deluxe Suite. That's for 1 guest. Your confirmation number is 12345, just in case you need it.

        So, just a quick reminder, check-in is at 3 PM, and check-out is at, well, 11 AM.

        Now, just a heads-up about our cancellation policy… if you need to cancel, just let us know at least 48 hours before your arrival, okay? Otherwise, there'll be a charge for one night's stay.

        And to make your stay even better, you'll have complimentary Wi-Fi, access to our fitness center, and a delicious complimentary breakfast each morning!

        If you have any questions at all, please don't hesitate to call us at 855-555-6689. We can't wait to welcome you to the hotel!"

        Explanation of Changes:
            The ellipses (...) create a pause for emphasis.
            "and we've" uses a contraction for a more conversational tone.
            "It's, well, it's very exciting" adds a small amount of disfluency, and emphasis.
            "Okay?" friendly reminder softens tone.

    By following these guidelines, you can create text-to-audio scripts that sound natural, engaging, and human-like. Remember that practice and experimentation are key to mastering this skill.

Chirp 3: HD voice controls

Preview

This product or feature is subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the Service Specific Terms. Pre-GA products and features are available "as is" and might have limited support. For more information, see the launch stage descriptions.

Voice control features are specifically for HD voice synthesis. You can manage pace control, pause control, and custom pronunciations through the Chirp 3: HD voice control options.
Pace control

You can adjust the speed of the generated audio using the pace parameter. The pace parameter lets you slow down or speed up the speech, with values ranging from 0.25x (very slow) to 2x (very fast). To set the pace, use the speaking_rate parameter in your request. Choose a value between 0.25 and 2.0. Values below 1.0 slow down the speech, and values above 1.0 speed it up. A value of 1.0 indicates an unadjusted pace.

Pause control

You can insert pauses into AI-generated speech by embedding special tags directly into your text using the markup input field. Note that pause tags will only work in the markup field, and not in the text field.

These tags signal the AI to create silences, but the precise length of these pauses isn't fixed. The AI adjusts the duration based on context, much like natural human speech varies with speaker, location, and sentence structure. The available pause tags are [pause short], [pause long], and [pause]. For alternative methods of creating pauses without using markup tags, refer to our prompting and crafting guidelines.

The AI model might occasionally disregard the pause tags, especially if they are placed in unnatural positions in the text. You can combine multiple pause tags for longer silences, but excessive use can lead to problems.

Pause control audio samples:
Markup input 	Output
"Let me take a look, yes, I see it." 	
"Let me take a look, [pause long] yes, I see it."

Custom pronunciations

You can specify custom pronunciations using IPA or X-SAMPA phonetic representations for words within the input text. Be sure to use language-appropriate phonemes for accurate rendering. You can learn more about phoneme override in our phoneme documentation.

The overridden phrases can be formatted in any way, including using symbols. For example, in case of potential context-based ambiguity in phrase matching (which is common in languages like Chinese and Japanese) or sentences where one word might be pronounced in different ways, the phrase can be formatted to remove ambiguity. For example, to avoid accidentally overriding other instances of the word read in the input, the phrase "read" could be formatted as "read1", "[read]", or "(read)" for both the input text and the overridden phrase.
"""