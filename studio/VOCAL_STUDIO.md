# Original Vocal Song Studio

This is the **AI full-song** pipeline, distinct from the basic procedural instrumental demo.

## Run
1. Start an ACE-Step 1.5 API server on hardware you control or have permission to use. Official upstream: https://github.com/ace-step/ACE-Step-1.5 . The server must be reachable via HTTPS from GitHub Actions.
2. In GitHub repository Settings > Secrets and variables > Actions, add `ACESTEP_API_URL` with the server's HTTPS base URL (for example, `https://your-secure-server.example`). If the server uses authentication, add `ACESTEP_API_KEY`.
3. Edit `studio/song.json` to set original lyrics and production direction.
4. Go to Actions > **Original Vocal Song (ACE-Step)** > Run workflow. After completion, download the MP3 artifact.

**Do not put credentials in workflow files or commits.** Secure the API with HTTPS and authentication. The code accepts only audio files returned by the configured server.

## Important limitations
- This pipeline **requires an actual ACE-Step server**. A standard GitHub-hosted runner has no GPU to run ACE-Step at this quality. GitHub Actions alone cannot guarantee free, unlimited GPU generation.
- The model generates music *including vocals* based on the prompt and lyrics; exact human realism, commercial hit quality, timing, and intelligibility are not guaranteed. Listen and review before publishing.
- The final audio is normalized to 59 seconds by trimming/padding and 1.2-second fades. It is possible for the model to place part of a lyric after the cut.
- The ACE-Step project is open-source, but confirm the applicable model weights, third-party assets, and deployment terms before commercial distribution.
- This workflow creates **audio only**. The older `original-music-studio.yml` workflow remains a procedural instrumental + graphic-video demo. Cinematic generative video is not yet implemented.
