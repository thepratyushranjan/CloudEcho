import { getMCPStatus } from "../node_app/services/mcpStatusService.js";
import { writeJsonToStdout, writeErrorAndExit } from "./common.mjs";

(async () => {
  try {
    const status = await getMCPStatus();
    writeJsonToStdout(status);
  } catch (err) {
    writeErrorAndExit(err);
  }
})();
