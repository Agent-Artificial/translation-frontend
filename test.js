const fs = require('fs');
const { json } = require('stream/consumers');
const axois = require("axios");
// Assuming 'audioData' is the base64-encoded string received from the backend

async function getAudioData() {
    // Get the audio data from the backend
    body = {
        data: {
            input: "hello world",
            task_string: "text2speech",
            target_language: "french",
            source_language: "english",
        }
    }
    return await fetch("https://miner-cellium.ngrok.app/modules/translation/process", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    }).then((response) => response.text());
}

async function convert() {
    audioData = await getAudioData();
    console.log(audioData);
    return await fetch("https://translation-cellium.ngrok.app/torch", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(audioData),
    }).then((response) => response.text());
}

// Usage:
// Assuming you've received the base64-encoded audio data from the backend
async function main() {
    audioData = await convert();
    console.log(audioData);
}

(async () => {await main()})()