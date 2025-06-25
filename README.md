# Chess Game Project: Evolution from v1 to v2

This project showcases the complete evolution of a Chess Game developed in Python, demonstrating a significant transition from its original Button-based implementation (**v1**) to a highly sophisticated, AI-driven, Canvas-based application (**v2**). The purpose of this project is not only to create an interactive and challenging Chess experience but also to highlight advances in software design, AI learning, and game mechanics.

## Project Evolution and Architecture Comparison

| Feature                     | v1: Button-Based Game                            | v2: Canvas-Based AI Game                                                                             |
| --------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| **User Interface**          | Developed with Tkinter Buttons and Frames        | Created using Tkinter Canvas for visual design and responsiveness                                    |
| **Move Execution**          | Moves selected via Button clicks                 | Moves selected via Mouse click events with graphical feedback                                        |
| **Artificial Intelligence** | Random move generation with basic state checking | AI enhanced with a JSON-backed learning mechanism, making its moves evolve based on prior experience |
| **Move Validation**         | Simple rule-based approach for valid moves       | Detailed FEN-based state parsing, robust rule enforcement, and advanced move generation              |
| **UI Highlighting**         | Button background changes for highlighting       | Graphical overlay (circles) that visually denotes valid moves                                        |
| **Additional Features**     | Sound effects for moves, basic promotion support | i leave it same                                                                                      |
| **Learning Capabilities**   | None (no state saved)                            | Incorporation of move recording and caching for long-term AI improvement                             |

## Why the New Version Stands Out

* Enables a sophisticated AI experience that evolves with the player.
* Incorporates a robust, state-driven FEN system for precision move generation and detection.
* Provides enhanced visual feedback and a more engaging user experience.
* Supports a more extensible architecture for future advances, making it ideal for further AI research and interactive implementations.

## Roadmap

* **Future AI Enhancements:** Integration with deep learning or reinforcement learning algorithms.
* **Networking Capabilities:** Support for multiplayer online play. (Maybe)
* **Modern User Experience:** Responsive design for mobile platforms and extended accessibility.

**Final Thoughts:** This project is a starter project for me to get used to machine learning and neural network based algorytms simply but also im lazy :)


## Known Bugs

*At the few beggining games ai is not aware if the queen is checked and you have to actually capture it to checkmate but due to this ai is a "learning" (record/analyse for next games) based system its now happen on later stages
*pawns have 2 square moves everytime (currently working on fixing that)
*sometimes doesnt let you castle (currently working on fixing that)
*

> "From humble beginnings to a sophisticated learning AI — this is the roadmap of innovation in game design."
