(function () {
    "use strict";

    /*
    ============================================================
    PENTRAone AGRICULTURE - SARVAM INDIAN VOICE AGENT
    ============================================================

    This replaces browser speechSynthesis.

    Languages:
        English  -> en-IN
        Hindi    -> hi-IN
        Marathi  -> mr-IN
        Gujarati -> gu-IN
        Bengali  -> bn-IN
        Tamil    -> ta-IN
        Telugu   -> te-IN
        Kannada  -> kn-IN
        Punjabi  -> pa-IN
    ============================================================
    */

    const VOICE_ENDPOINT = "/agriculture/voice/";

    const LANGUAGE_CODES = {
        en: "en",
        hi: "hi",
        mr: "mr",
        gu: "gu",
        bn: "bn",
        ta: "ta",
        te: "te",
        kn: "kn",
        pa: "pa"
    };

    const LABELS = {
        en: {
            listen: "Listen",
            stop: "Stop",
            loading: "Preparing voice...",
            noText: "There is no information to read.",
            error: "Voice service is unavailable. Please try again."
        },

        hi: {
            listen: "सुनें",
            stop: "रोकें",
            loading: "आवाज़ तैयार हो रही है...",
            noText: "पढ़ने के लिए कोई जानकारी नहीं है।",
            error: "वॉइस सेवा अभी उपलब्ध नहीं है। कृपया फिर कोशिश करें।"
        },

        mr: {
            listen: "ऐका",
            stop: "थांबवा",
            loading: "आवाज तयार होत आहे...",
            noText: "वाचण्यासाठी माहिती उपलब्ध नाही.",
            error: "आवाज सेवा सध्या उपलब्ध नाही. कृपया पुन्हा प्रयत्न करा."
        },

        gu: {
            listen: "સાંભળો",
            stop: "બંધ કરો",
            loading: "અવાજ તૈયાર થઈ રહ્યો છે...",
            noText: "વાંચવા માટે માહિતી નથી.",
            error: "અવાજ સેવા હાલમાં ઉપલબ્ધ નથી. ફરી પ્રયાસ કરો."
        },

        bn: {
            listen: "শুনুন",
            stop: "থামান",
            loading: "ভয়েস প্রস্তুত হচ্ছে...",
            noText: "পড়ার জন্য কোনো তথ্য নেই।",
            error: "ভয়েস পরিষেবা এখন উপলব্ধ নয়। আবার চেষ্টা করুন।"
        },

        ta: {
            listen: "கேளுங்கள்",
            stop: "நிறுத்து",
            loading: "குரல் தயாராகிறது...",
            noText: "படிக்க தகவல் இல்லை.",
            error: "குரல் சேவை தற்போது கிடைக்கவில்லை. மீண்டும் முயற்சிக்கவும்."
        },

        te: {
            listen: "వినండి",
            stop: "ఆపండి",
            loading: "వాయిస్ సిద్ధమవుతోంది...",
            noText: "చదవడానికి సమాచారం లేదు.",
            error: "వాయిస్ సేవ ప్రస్తుతం అందుబాటులో లేదు. మళ్లీ ప్రయత్నించండి."
        },

        kn: {
            listen: "ಕೇಳಿ",
            stop: "ನಿಲ್ಲಿಸಿ",
            loading: "ಧ್ವನಿ ಸಿದ್ಧವಾಗುತ್ತಿದೆ...",
            noText: "ಓದಲು ಮಾಹಿತಿ ಇಲ್ಲ.",
            error: "ಧ್ವನಿ ಸೇವೆ ಈಗ ಲಭ್ಯವಿಲ್ಲ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
        },

        pa: {
            listen: "ਸੁਣੋ",
            stop: "ਰੋਕੋ",
            loading: "ਆਵਾਜ਼ ਤਿਆਰ ਹੋ ਰਹੀ ਹੈ...",
            noText: "ਪੜ੍ਹਨ ਲਈ ਕੋਈ ਜਾਣਕਾਰੀ ਨਹੀਂ ਹੈ।",
            error: "ਆਵਾਜ਼ ਸੇਵਾ ਇਸ ਸਮੇਂ ਉਪਲਬਧ ਨਹੀਂ ਹੈ। ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।"
        }
    };


    let activeButton = null;
    let activeAudio = null;
    let activeObjectUrl = null;
    let activeAbortController = null;


    /*
    ============================================================
    LANGUAGE
    ============================================================
    */

    function normalizeLanguage(language) {

        if (!language) {
            return "en";
        }

        let value = String(language)
            .trim()
            .toLowerCase();

        const fullNames = {
            english: "en",
            hindi: "hi",
            marathi: "mr",
            gujarati: "gu",
            bengali: "bn",
            tamil: "ta",
            telugu: "te",
            kannada: "kn",
            punjabi: "pa"
        };

        if (fullNames[value]) {
            value = fullNames[value];
        }

        if (value.includes("-")) {
            value = value.split("-")[0];
        }

        return LANGUAGE_CODES[value]
            ? value
            : "en";
    }


    function getLabels(language) {
        return LABELS[
            normalizeLanguage(language)
        ] || LABELS.en;
    }


    /*
    ============================================================
    CSRF
    ============================================================
    */

    function getCookie(name) {

        const cookies =
            document.cookie
                .split(";")
                .map(function (cookie) {
                    return cookie.trim();
                });

        for (const cookie of cookies) {

            if (
                cookie.startsWith(name + "=")
            ) {
                return decodeURIComponent(
                    cookie.substring(
                        name.length + 1
                    )
                );
            }
        }

        return "";
    }


    /*
    ============================================================
    BUTTON STATE
    ============================================================
    */

    function setButton(button, state) {

        if (!button) {
            return;
        }

        const language =
            normalizeLanguage(
                button.dataset.voiceLanguage ||
                button.dataset.voiceLang
            );

        const labels =
            getLabels(language);

        const label =
            button.querySelector(
                "[data-voice-label]"
            );

        button.classList.toggle(
            "is-speaking",
            state === "speaking"
        );

        button.classList.toggle(
            "is-loading",
            state === "loading"
        );

        button.setAttribute(
            "aria-busy",
            state === "loading" ? "true" : "false"
        );

        button.setAttribute(
            "aria-pressed",
            state === "speaking" ? "true" : "false"
        );

        if (state === "loading") {

            button.setAttribute(
                "aria-label",
                labels.loading
            );

            if (label) {
                label.textContent =
                    labels.loading;
            } else {
                button.textContent =
                    "⏳ " + labels.loading;
            }

            return;
        }

        if (state === "speaking") {

            button.setAttribute(
                "aria-label",
                labels.stop
            );

            if (label) {
                label.textContent =
                    labels.stop;
            } else {
                button.textContent =
                    "⏹ " + labels.stop;
            }

            return;
        }

        button.setAttribute(
            "aria-label",
            labels.listen
        );

        if (label) {
            label.textContent =
                labels.listen;
        } else {
            button.textContent =
                "🔊 " + labels.listen;
        }
    }


    /*
    ============================================================
    STATUS
    ============================================================
    */

    function setStatus(button, message) {

        if (!button) {
            return;
        }

        const parent =
            button.parentElement;

        if (!parent) {
            return;
        }

        const status =
            parent.querySelector(
                "[data-voice-status]"
            );

        if (status) {
            status.textContent =
                message || "";
        }
    }


    /*
    ============================================================
    TEXT CLEANING
    ============================================================
    */

    function cleanText(elements) {

        const list =
            Array.isArray(elements)
                ? elements
                : [elements];

        return list
            .map(function (element) {

                const clone =
                    element.cloneNode(true);

                clone
                    .querySelectorAll(
                        "script,style,button,input,textarea,select,[aria-hidden='true']"
                    )
                    .forEach(function (el) {
                        el.remove();
                    });

                return (
                    clone.innerText ||
                    clone.textContent ||
                    ""
                );
            })
            .join(" ")
            .replace(
                /[\u{1F300}-\u{1FAFF}]/gu,
                ""
            )
            .replace(
                /[\u2600-\u27BF]/g,
                ""
            )
            .replace(
                /[#*_`~]/g,
                ""
            )
            .replace(
                /\s+/g,
                " "
            )
            .replace(
                /\s+([,.!?;:])/g,
                "$1"
            )
            .trim();
    }


    /*
    ============================================================
    TEXT CHUNKING
    ============================================================
    */

    function splitText(
        text,
        maxLength = 2200
    ) {

        const sentences =
            text.match(
                /[^.!?।॥！？]+[.!?।॥！？]?/g
            ) || [text];

        const result = [];

        let current = "";


        sentences.forEach(
            function (sentence) {

                sentence =
                    sentence.trim();

                if (!sentence) {
                    return;
                }

                const candidate =
                    (
                        current +
                        " " +
                        sentence
                    ).trim();

                if (
                    candidate.length <=
                    maxLength
                ) {

                    current =
                        candidate;

                    return;
                }


                if (current) {
                    result.push(current);
                }


                if (
                    sentence.length <=
                    maxLength
                ) {

                    current =
                        sentence;

                    return;
                }


                for (
                    let i = 0;
                    i < sentence.length;
                    i += maxLength
                ) {

                    result.push(
                        sentence
                            .slice(
                                i,
                                i + maxLength
                            )
                            .trim()
                    );
                }

                current = "";
            }
        );


        if (current) {
            result.push(current);
        }

        return result.filter(Boolean);
    }


    /*
    ============================================================
    TARGET CONTENT
    ============================================================
    */

    function getTargetText(button) {

        const selector =
            button.dataset.voiceTarget;

        if (!selector) {
            return "";
        }

        let targets = [];

        try {

            targets =
                Array.from(
                    document.querySelectorAll(
                        selector
                    )
                );

        } catch (error) {

            console.warn(
                "Voice target selector error:",
                error
            );

            return "";
        }

        if (!targets.length) {
            return "";
        }

        return cleanText(targets);
    }


    /*
    ============================================================
    STOP
    ============================================================
    */

    function stop() {

        if (activeAbortController) {

            activeAbortController.abort();

            activeAbortController =
                null;
        }


        if (activeAudio) {

            activeAudio.pause();

            activeAudio.currentTime = 0;

            activeAudio.src = "";

            activeAudio = null;
        }


        if (activeObjectUrl) {

            URL.revokeObjectURL(
                activeObjectUrl
            );

            activeObjectUrl = null;
        }


        if (activeButton) {

            setButton(
                activeButton,
                "idle"
            );

            setStatus(
                activeButton,
                ""
            );
        }


        activeButton = null;
    }


    /*
    ============================================================
    GENERATE ONE AUDIO CHUNK
    ============================================================
    */

    async function generateAudio(
        text,
        language
    ) {

        const csrfToken =
            getCookie("csrftoken");

        const controller =
            new AbortController();

        activeAbortController =
            controller;


        const response =
            await fetch(
                VOICE_ENDPOINT,
                {
                    method: "POST",

                    credentials: "same-origin",

                    headers: {
                        "Content-Type":
                            "application/json",

                        ...(csrfToken
                            ? {
                                "X-CSRFToken":
                                    csrfToken
                            }
                            : {})
                    },

                    body: JSON.stringify({
                        text: text,
                        language: language
                    }),

                    signal:
                        controller.signal
                }
            );


        if (!response.ok) {

            let errorMessage =
                "Voice generation failed.";

            try {

                const data =
                    await response.json();

                if (data && data.error) {
                    errorMessage =
                        data.error;
                }

            } catch (error) {
                // Ignore JSON parsing failure.
            }

            throw new Error(
                errorMessage
            );
        }


        return await response.blob();
    }


    /*
    ============================================================
    PLAY CHUNKS
    ============================================================
    */

    async function playChunks(
        button,
        chunks,
        language
    ) {

        for (
            let index = 0;
            index < chunks.length;
            index++
        ) {

            if (
                activeButton !== button
            ) {
                return;
            }


            setStatus(
                button,
                `${index + 1} / ${chunks.length}`
            );


            const blob =
                await generateAudio(
                    chunks[index],
                    language
                );


            if (
                activeButton !== button
            ) {
                return;
            }


            if (activeObjectUrl) {

                URL.revokeObjectURL(
                    activeObjectUrl
                );
            }


            activeObjectUrl =
                URL.createObjectURL(blob);


            const audio =
                new Audio(
                    activeObjectUrl
                );

            audio.preload = "auto";

            activeAudio =
                audio;

            setButton(
                button,
                "speaking"
            );


            await new Promise(
                function (resolve, reject) {

                    let settled = false;

                    function finishResolve() {

                        if (settled) {
                            return;
                        }

                        settled = true;

                        resolve();
                    }

                    function finishReject(
                        error
                    ) {

                        if (settled) {
                            return;
                        }

                        settled = true;

                        reject(error);
                    }


                    audio.onended =
                        function () {
                            finishResolve();
                        };


                    audio.onerror =
                        function () {

                            finishReject(
                                new Error(
                                    "Audio playback failed."
                                )
                            );

                        };


                    audio.onpause =
                        function () {

                            if (
                                activeButton !==
                                button
                            ) {
                                finishResolve();
                            }

                        };


                    audio
                        .play()
                        .catch(
                            function (error) {
                                finishReject(
                                    error
                                );
                            }
                        );
                }
            );


            if (
                activeObjectUrl
            ) {

                URL.revokeObjectURL(
                    activeObjectUrl
                );

                activeObjectUrl =
                    null;
            }

            activeAudio = null;


            if (
                activeButton !== button
            ) {
                return;
            }
        }
    }


    /*
    ============================================================
    START
    ============================================================
    */

    async function start(button) {

        if (!button) {
            return;
        }


        const language =
            normalizeLanguage(
                button.dataset.voiceLanguage ||
                button.dataset.voiceLang
            );

        const labels =
            getLabels(language);


        const text =
            getTargetText(button);


        if (!text) {

            setStatus(
                button,
                labels.noText
            );

            return;
        }


        stop();


        activeButton =
            button;

        setButton(
            button,
            "loading"
        );

        setStatus(
            button,
            labels.loading
        );


        const chunks =
            splitText(text, 2200);


        try {

            await playChunks(
                button,
                chunks,
                language
            );


            if (
                activeButton === button
            ) {

                setButton(
                    button,
                    "idle"
                );

                setStatus(
                    button,
                    ""
                );

                activeButton =
                    null;
            }

        } catch (error) {

            if (
                error &&
                error.name ===
                "AbortError"
            ) {
                return;
            }


            console.error(
                "Agriculture Voice Agent:",
                error
            );


            if (
                activeButton === button
            ) {

                setButton(
                    button,
                    "idle"
                );

                setStatus(
                    button,
                    labels.error
                );

                activeButton =
                    null;
            }
        }
    }


    /*
    ============================================================
    BUTTON BINDING
    ============================================================
    */

    function bind() {

        /*
        Supports both our older and newer button markup.
        */

        const buttons =
            document.querySelectorAll(
                "[data-voice-button], [data-voice-reader]"
            );


        buttons.forEach(
            function (button) {

                if (
                    button.dataset.voiceBound ===
                    "1"
                ) {
                    return;
                }


                button.dataset.voiceBound =
                    "1";


                setButton(
                    button,
                    "idle"
                );


                button.addEventListener(
                    "click",
                    function (event) {

                        event.preventDefault();


                        if (
                            activeButton ===
                            button
                        ) {

                            stop();

                            return;
                        }


                        start(button);
                    }
                );
            }
        );
    }


    /*
    ============================================================
    PAGE LOAD
    ============================================================
    */

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            bind
        );

    } else {

        bind();
    }


    /*
    ============================================================
    PUBLIC API
    ============================================================
    */

    window.PentraoneAgricultureVoice = {
        start: start,
        stop: stop,
        bind: bind
    };

})();