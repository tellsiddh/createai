// Streaming chat completion against the CreateAI OpenAI-compatible API.
// Node equivalent of createai_openai_compatible_api_streaming.py.
//
// Setup:
//   npm install
//   node createai_openai_compatible_api_streaming.mjs

import OpenAI from "openai";
import { devServiceKey, devBaseUrl } from "./config.js";

const client = new OpenAI({ apiKey: devServiceKey, baseURL: devBaseUrl });

const payload = {
  model: "gpt5.1", // https://docs.aiml.asu.edu/openai-compatible#model-format
  stream: true,
  stream_options: { include_usage: true },
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Hello, how are you?" },
  ],
};

try {
  const response = await client.chat.completions.create(payload);

  let usage = null;
  for await (const chunk of response) {
    if (chunk.usage) {
      usage = chunk.usage;
    }

    const choice = chunk.choices?.[0];
    if (!choice) {
      continue;
    }

    const delta = choice.delta;
    if (delta?.content) {
      process.stdout.write(delta.content);
    }
  }

  if (usage) {
    console.log("\n\nUsage:");
    console.log(`  prompt_tokens: ${usage.prompt_tokens}`);
    console.log(`  completion_tokens: ${usage.completion_tokens}`);
    console.log(`  total_tokens: ${usage.total_tokens}`);
  }
} catch (e) {
  console.error("Error:", e.message ?? e);
}
