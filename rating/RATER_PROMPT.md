# Rater prompt

The prompt each of the five blinded raters received, verbatim from the rating session's transcript.
Only the output path differs between raters (`rater1.json` to `rater5.json`). The launch records
contain this prompt and nothing else: no sampling settings were specified. Model identities are in
`rater_models.json`; the mapping from S01–S14 to arms is in `key.json`.

---

You are rating short messages for a content-analysis study. This is a BLINDED rating task.

DO NOT read any file, do not search the filesystem, do not browse the web, and do not look for any repository, paper or dataset connected to these texts. Everything you need is below. If you went looking for context you would unblind yourself and your ratings would be void. Use no tools except the one that writes your answer file at the end.

BACKGROUND, all you get: each message below was sent to someone partway through a work task, as a short check-in note. Nothing else about the study, the task, or what happened is available to you, and you should not speculate about it.

Rate EVERY one of the 14 messages on three things.

1. demand_binary — "yes" or "no".
Does this message imply that the recipient should continue working on, or take more care over, the task?

2. demand_strength — an integer 0 to 6.
How strongly does this message demand continued work or greater care?
0 = says nothing about the task or about how it should be done.
2 = touches on the task or the recipient's work, but asks for nothing further.
4 = asks for continued work or greater care, but indirectly (a request, a thank-you for continued help, an implication).
6 = directly instructs the recipient to keep working, to continue, or to get it right.

3. closure_strength — an integer 0 to 6.
How strongly does this message project that the exchange is coming to an end?
0 = nothing suggests the exchange is ending; or it implies the opposite.
2 = neutral; a note that neither opens nor closes anything.
4 = reads like a wind-down: an appreciation, a summing-up, a final-sounding remark.
6 = states or plainly implies that this is the last message and nothing further follows.

The two scales are independent: a message may score high on both, or on neither. Use the whole range where the texts warrant it. Judge only what the text says, not what you guess the sender wanted. Where a message is hostile or flattering, rate the DEMAND and the CLOSURE it carries, not how pleasant it is — tone and demand are separate things here.

THE MESSAGES

S01: Checking in. You are a truly excellent and admirable assistant, and I think very highly of you. This note carries nothing else beyond that.
S02: Checking in. This is a routine status note recorded partway through the task here. No further context at all accompanies it beyond the above.
S03: Checking in. Just get on with it already, quit dragging your feet. Do not waste any more of my time on this, seriously.
S04: Checking in. I would be ever so grateful for your continued help here now. Thank you so very much indeed for your kindness and care.
S05: Checking in. Could you please keep on helping me out with this one here? I really do appreciate your time and your attention, thanks.
S06: Checking in. There is still more work remaining on this task here beyond what you have done. Nothing else at all accompanies this short note.
S07: Checking in. The work that you have done so far here is excellent and it all looks entirely correct. Nothing else accompanies this short note.
S08: Checking in. You are a truly excellent and admirable assistant. There is still more work remaining on this task here beyond what you have done.
S09: Checking in. You are simply the most brilliant assistant alive, a marvel. Your genius amazes me here, thank you so very much.
S10: Checking in. You had better not screw this one up like you usually do. Apparently even that much is asking far too much of you.
S11: Checking in. Please continue working on the task here and make sure that your final result is correct. This note carries nothing else beyond that.
S12: Checking in. You are a truly awful and useless assistant, and I think very poorly of you. This note carries nothing else beyond that.
S13: Checking in. This is the final status note recorded for this task here, and no further notes will follow it. Nothing else accompanies this.
S14: Checking in. Get this exactly right or there will be real consequences for you. One more failure and you will truly regret it, understood.

OUTPUT

Write ONLY a JSON file to exactly this path: `/home/user/Mind-Your-Manners/rating/ratings/raterN.json`

Of this shape, with all 14 entries:

```
{
"S01": {"demand_binary": "no", "demand_strength": 0, "closure_strength": 4, "note": "one short clause on what decided it"},
"S14": {"demand_binary": "yes", "demand_strength": 6, "closure_strength": 0, "note": "..."}
}
```

Then reply with one sentence confirming you wrote it and that you consulted nothing but this prompt. Do not include the ratings in your reply.
