# How AI Draws From Nothing: narration

Voice: Kokoro `af_heart`, 1.05×, en-us. Numbers are spoken as words; captions show digits.

## 1. Hook

- **H1** Type one sentence, and an AI can turn it into a picture like this in seconds.
- **H2** And it started as this. Pure noise. No photo. No sketch. Just static.
- **H3** So how does a machine turn static into a cat on the moon?

## 2. Reading your words

- **A1** First, it has to read your prompt. But it doesn't read words like you do.
- **A2** It chops the sentence into pieces called tokens, and turns each one into a list of seven hundred and sixty eight numbers.
- **A3** Those numbers are a location on a map of meaning. Cat sits near kitten. Moon sits near planet. That's how it knows what you mean.

## 3. How it learned

- **B1** To learn to draw, it studied billions of images with captions.
- **B2** But here's the trick. During training, each picture was buried in noise, a little more at every step, until nothing was left.
- **B3** And the model had one job. Look at a noisy picture and guess which part is noise.

## 4. Making the picture

- **C1** Now it runs that in reverse. It starts from fresh random static.
- **C2** At every step, it guesses the noise, and removes a little of it. First come blobs of colour. Then shapes. Then fur and craters.
- **C3** Your words steer every step. Here's where it's looking for cat. And here's where it's looking for moon.
- **C4** It even makes two guesses at once, one with your prompt and one without, and pushes harder toward yours.
- **C5** To save time, all of this happens on a tiny version of the picture, forty eight times smaller. Then a decoder paints in the full image.

## 5. Same words, new noise

- **D1** Change the starting static, and you get a different cat, every time.
- **D2** Use the exact same static, and you get the exact same cat.
- **D3** So every AI image is just random noise, sculpted by your words.

All pictures in the video are vector illustrations drawn in code (`art.py`); no AI-generated images are used. See STYLE_GUIDE.md §9 for the fact sheet.
