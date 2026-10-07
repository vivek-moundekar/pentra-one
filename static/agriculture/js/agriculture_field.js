(function () {
    "use strict";

    /*
     * UDAAN AGRICULTURE
     * Interactive Grass / Crop Field
     *
     * - Grass gently moves on its own
     * - Grass reacts to mouse movement
     * - Cursor creates a soft "wind" effect
     * - Does not block clicks
     * - Works with light/dark mode
     * - Automatically reduces itself on small screens
     */

    if (window.__UDAAN_FIELD_INITIALIZED__) {
        return;
    }

    window.__UDAAN_FIELD_INITIALIZED__ = true;


    /* =========================================================
       SETTINGS
       ========================================================= */

    const CONFIG = {
        desktopDensity: 150,
        tabletDensity: 90,

        mouseRadius: 120,

        mouseStrength: 1.7,

        naturalWind: 0.35,

        animationSpeed: 0.018,

        opacity: 0.55,

        zIndex: 0
    };


    /* =========================================================
       MOBILE CHECK
       ========================================================= */

    function isMobile() {
        return window.innerWidth <= 700;
    }

    function isTablet() {
        return window.innerWidth > 700 &&
               window.innerWidth <= 1100;
    }


    /* =========================================================
       CANVAS
       ========================================================= */

    const canvas = document.createElement("canvas");

    canvas.id = "udaan-agriculture-field";

    canvas.setAttribute(
        "aria-hidden",
        "true"
    );

    canvas.style.position = "fixed";
    canvas.style.left = "0";
    canvas.style.top = "0";
    canvas.style.width = "100%";
    canvas.style.height = "100%";
    canvas.style.pointerEvents = "none";
    canvas.style.zIndex = String(CONFIG.zIndex);
    canvas.style.opacity = String(CONFIG.opacity);

    document.body.appendChild(canvas);


    const ctx = canvas.getContext("2d");

    if (!ctx) {
        return;
    }


    /* =========================================================
       STATE
       ========================================================= */

    let width = 0;
    let height = 0;

    let grass = [];

    let animationFrame = null;

    let mouse = {
        x: -9999,
        y: -9999,
        active: false
    };


    /* =========================================================
       RESIZE
       ========================================================= */

    function resizeCanvas() {

        width = window.innerWidth;
        height = window.innerHeight;

        const dpr = Math.min(
            window.devicePixelRatio || 1,
            2
        );

        canvas.width = width * dpr;
        canvas.height = height * dpr;

        ctx.setTransform(
            dpr,
            0,
            0,
            dpr,
            0,
            0
        );

        createGrass();
    }


    /* =========================================================
       GRASS CREATION
       ========================================================= */

    function createGrass() {

        grass = [];

        if (isMobile()) {
            return;
        }

        let density = CONFIG.desktopDensity;

        if (isTablet()) {
            density = CONFIG.tabletDensity;
        }

        /*
         * Spread grass across the bottom part
         * of the screen.
         */

        const spacing = width / density;

        for (let x = -20; x < width + 20; x += spacing) {

            const blade = {

                x: x + random(-8, 8),

                baseY:
                    height -
                    random(
                        isTablet() ? 45 : 65,
                        isTablet() ? 110 : 145
                    ),

                height:
                    random(
                        isTablet() ? 22 : 28,
                        isTablet() ? 65 : 90
                    ),

                width:
                    random(1, 2.5),

                lean:
                    random(-0.25, 0.25),

                phase:
                    random(0, Math.PI * 2),

                speed:
                    random(0.7, 1.3),

                bend: 0,

                bendVelocity: 0,

                seed:
                    Math.random()

            };

            grass.push(blade);
        }
    }


    /* =========================================================
       RANDOM
       ========================================================= */

    function random(min, max) {

        return Math.random() *
            (max - min) +
            min;
    }


    /* =========================================================
       MOUSE
       ========================================================= */

    function updateMouse(event) {

        mouse.x = event.clientX;
        mouse.y = event.clientY;

        mouse.active = true;
    }


    function resetMouse() {

        mouse.active = false;

        mouse.x = -9999;
        mouse.y = -9999;
    }


    window.addEventListener(
        "mousemove",
        updateMouse,
        {
            passive: true
        }
    );


    window.addEventListener(
        "mouseleave",
        resetMouse
    );


    /* =========================================================
       DRAW ONE GRASS BLADE
       ========================================================= */

    function drawBlade(blade, time) {

        const x = blade.x;

        const baseY = blade.baseY;

        const h = blade.height;

        /*
         * Natural wind movement
         */

        const natural =
            Math.sin(
                time *
                CONFIG.animationSpeed *
                blade.speed +
                blade.phase
            ) *
            CONFIG.naturalWind;


        /*
         * Cursor interaction
         */

        let cursorBend = 0;

        if (mouse.active) {

            const dx =
                mouse.x - blade.x;

            const dy =
                mouse.y - baseY;

            const distance =
                Math.sqrt(
                    dx * dx +
                    dy * dy
                );

            if (
                distance <
                CONFIG.mouseRadius
            ) {

                const influence =
                    1 -
                    distance /
                    CONFIG.mouseRadius;

                /*
                 * Push grass away from cursor.
                 */

                const direction =
                    dx >= 0
                        ? -1
                        : 1;

                cursorBend =
                    direction *
                    influence *
                    CONFIG.mouseStrength;
            }
        }


        /*
         * Smooth physics
         */

        const targetBend =
            natural +
            cursorBend +
            blade.lean;


        blade.bendVelocity +=
            (targetBend - blade.bend) *
            0.08;

        blade.bendVelocity *= 0.82;

        blade.bend +=
            blade.bendVelocity;


        /*
         * Grass shape
         */

        const tipX =
            x +
            blade.bend *
            h;

        const tipY =
            baseY - h;


        /*
         * Slight middle curve
         */

        const controlX =
            x +
            blade.bend *
            h *
            0.45;

        const controlY =
            baseY -
            h *
            0.55;


        /*
         * Theme detection
         */

        const dark =
            document.documentElement
                .classList
                .contains("dark") ||
            document.body.classList
                .contains("dark") ||
            document.body.classList
                .contains("dark-mode");


        /*
         * Draw blade
         */

        ctx.beginPath();

        ctx.moveTo(
            x,
            baseY
        );

        ctx.quadraticCurveTo(
            controlX,
            controlY,
            tipX,
            tipY
        );


        /*
         * Different green for theme.
         */

        if (dark) {

            ctx.strokeStyle =
                blade.seed > 0.55
                    ? "rgba(110, 190, 92, 0.55)"
                    : "rgba(75, 160, 70, 0.45)";

        } else {

            ctx.strokeStyle =
                blade.seed > 0.55
                    ? "rgba(50, 140, 65, 0.48)"
                    : "rgba(80, 160, 70, 0.38)";
        }


        ctx.lineWidth =
            blade.width;

        ctx.lineCap =
            "round";

        ctx.stroke();


        /*
         * Tiny second leaf on some blades
         */

        if (blade.seed > 0.72) {

            const leafStartX =
                x +
                blade.bend *
                h *
                0.38;

            const leafStartY =
                baseY -
                h *
                0.38;

            const leafEndX =
                leafStartX +
                blade.bend *
                18 -
                10;

            const leafEndY =
                leafStartY -
                14;


            ctx.beginPath();

            ctx.moveTo(
                leafStartX,
                leafStartY
            );

            ctx.quadraticCurveTo(
                leafStartX - 4,
                leafStartY - 10,
                leafEndX,
                leafEndY
            );

            ctx.strokeStyle =
                dark
                    ? "rgba(100, 180, 80, 0.38)"
                    : "rgba(60, 145, 65, 0.32)";

            ctx.lineWidth =
                Math.max(
                    0.8,
                    blade.width * 0.7
                );

            ctx.stroke();
        }
    }


    /* =========================================================
       DRAW SOFT FIELD GLOW
       ========================================================= */

    function drawFieldGlow() {

        const dark =
            document.documentElement
                .classList
                .contains("dark") ||
            document.body.classList
                .contains("dark-mode");


        const gradient =
            ctx.createLinearGradient(
                0,
                height - 180,
                0,
                height
            );


        if (dark) {

            gradient.addColorStop(
                0,
                "rgba(30, 100, 45, 0)"
            );

            gradient.addColorStop(
                1,
                "rgba(20, 80, 35, 0.08)"
            );

        } else {

            gradient.addColorStop(
                0,
                "rgba(70, 160, 70, 0)"
            );

            gradient.addColorStop(
                1,
                "rgba(70, 160, 70, 0.07)"
            );
        }


        ctx.fillStyle =
            gradient;

        ctx.fillRect(
            0,
            height - 180,
            width,
            180
        );
    }


    /* =========================================================
       ANIMATION
       ========================================================= */

    function animate(time) {

        if (isMobile()) {

            ctx.clearRect(
                0,
                0,
                width,
                height
            );

            animationFrame =
                requestAnimationFrame(
                    animate
                );

            return;
        }


        ctx.clearRect(
            0,
            0,
            width,
            height
        );


        drawFieldGlow();


        for (
            let i = 0;
            i < grass.length;
            i++
        ) {

            drawBlade(
                grass[i],
                time
            );
        }


        animationFrame =
            requestAnimationFrame(
                animate
            );
    }


    /* =========================================================
       START
       ========================================================= */

    function start() {

        resizeCanvas();

        if (animationFrame) {

            cancelAnimationFrame(
                animationFrame
            );
        }

        animationFrame =
            requestAnimationFrame(
                animate
            );
    }


    /* =========================================================
       WINDOW RESIZE
       ========================================================= */

    let resizeTimer;

    window.addEventListener(
        "resize",
        function () {

            clearTimeout(
                resizeTimer
            );

            resizeTimer =
                setTimeout(
                    resizeCanvas,
                    150
                );
        }
    );


    /* =========================================================
       REDUCE EFFECT WHEN TAB IS HIDDEN
       ========================================================= */

    document.addEventListener(
        "visibilitychange",
        function () {

            if (
                document.hidden
            ) {

                if (animationFrame) {

                    cancelAnimationFrame(
                        animationFrame
                    );

                    animationFrame =
                        null;
                }

            } else {

                if (!animationFrame) {

                    animationFrame =
                        requestAnimationFrame(
                            animate
                        );
                }
            }
        }
    );


    /* =========================================================
       START AFTER PAGE LOAD
       ========================================================= */

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            start
        );

    } else {

        start();
    }

})();