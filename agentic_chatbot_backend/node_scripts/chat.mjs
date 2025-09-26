import { runChatWorkflow } from "../node_app/services/chatService.js";
import { validateRequest } from "../node_app/utils/chatUtils.js";
import {
  readJsonFromStdin,
  writeJsonToStdout,
  writeErrorAndExit,
} from "./common.mjs";

(async () => {
  try {
    const payload = await readJsonFromStdin();
    const validated = validateRequest(payload);
    const chat = await runChatWorkflow({
      query: validated.query,
      history: validated.history,
    });
    writeJsonToStdout(chat.response);
  } catch (err) {
    writeErrorAndExit(err);
  }
})();
