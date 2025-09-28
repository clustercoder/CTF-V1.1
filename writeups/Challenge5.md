```
Challenge(
    id="envrn",
    title="6EQUJ5",
    description="search your env",
    flag_hash=hash_flag("GDG{codewithjoy}"),
    points=606,
)
```

---

### Walkthrough

- A video was displayed on the screen.  
- You’ll see a fullscreen canvas with some kind of animation.  
- At first, the canvas shows a **“NO SIGNAL” retro-TV background**.  
- Around the perimeter of the screen, you’ll notice small colored notches (in Google colors: blue, red, yellow, green).  
- These notches correspond to **letters A–Z placed around the screen edges**.  
- A mascot graphic appears.  
- It begins moving from notch to notch in sequence.  
- The mascot traces a word by moving to different notches (letters).  
- Watch carefully in order — each notch corresponds to a letter **A–Z**.  
- As the mascot moves, **write down the letters it lands on**.  
- After following the full cycle, the mascot completes a path that spells:  


---

### Flag
```python
flag_hash = hash_flag("GDG{codewithjoy}")
