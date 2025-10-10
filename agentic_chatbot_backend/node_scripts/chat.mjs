import { runChatWorkflow } from "../node_app/services/chatService.js";
import {
  validateRequest,
  streamChatEvents,
} from "../node_app/utils/chatUtils.js";
import {
  readJsonFromStdin,
  writeJsonToStdout,
  writeErrorAndExit,
} from "./common.mjs";

(async () => {
  try {
    const payload = await readJsonFromStdin();
    const wantsStream = Boolean(payload?.stream);
    const validated = validateRequest(payload);
    const chat = await runChatWorkflow({
      query: validated.query,
      history: validated.history,
      context: validated.context,
    });

    if (wantsStream) {
      const meta = chat.meta || {};
      for await (const line of streamChatEvents(
        {
          contentText: meta.contentText || chat.response?.result || "",
          reasoningText: meta.reasoningText || chat.response?.reasoning || null,
          result: meta.rawResult || chat.response || {},
         
        },
        { delayMs: 0 }
      )) {
        process.stdout.write(line);
      }
      return;
    }

    writeJsonToStdout(chat.response);
  } catch (err) {
    writeErrorAndExit(err);
  }
})();
