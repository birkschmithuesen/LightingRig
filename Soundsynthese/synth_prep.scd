s.meter;
s.plotTree;




(
SynthDef(\pipeWind1, {
    arg freq=440, amp=0.2, pan=0, gate=1;
    var noise, env, mod, sig;
    mod = LFNoise1.kr(0.2).range(-100, 100);
    noise = WhiteNoise.ar(1) * 0.5 + PinkNoise.ar(1) * 0.5;
    sig = BPF.ar(noise, freq + mod, 0.15);
    //env = EnvGen.kr(Env.adsr(0.5, 1.5, 0.3, 2), gate, doneAction: 2);
    sig = sig * (1 + SinOsc.kr(0.3, 0, 0.05));
    Out.ar(0, Pan2.ar(sig * amp, pan));
}).add;
)

(
SynthDef(\pipeWind2, {
    arg freq=440, amp=0.2, pan=0, gate=1;
    var noise, env, mod, rustMod, sig;
    mod = LFNoise1.kr(0.2).range(-100, 100);
    rustMod = LFNoise2.kr(1).range(-200, 200) * LFNoise1.kr(3).range(0.2, 0.8);
    breath = LPF.ar(WhiteNoise.ar(0.3), freq * 0.5) * LFNoise1.kr(2).range(0.2, 0.6);
    shimmer = HPF.ar(PinkNoise.ar(0.2), freq * 1.5) * LFNoise2.kr(5).range(0.1, 0.3);
    noise = WhiteNoise.ar(1) * 0.5 + PinkNoise.ar(1) * 0.5;
    sig = BPF.ar(noise, freq + mod + rustMod, 0.15);
    sig = sig.tanh * 0.5 + sig.distort * 0.5; // subtle distortion
    //env = EnvGen.kr(Env.adsr(0.5, 1.5, 0.3, 2), gate, doneAction: 2);
	sig = sig + 0.01 * RLPF.ar(LFPulse.ar([48,55].midicps, 0.15), SinOsc.kr(0.1, 0, 10, 72).midicps, 0.1, 0.1);
    sig = sig * (1 + SinOsc.kr(0.3, 0, 0.05));
    Out.ar(0, Pan2.ar(sig * amp, pan));
}).add;
)


x = Synth(\pipeWind2, [\freq, 400, \amp, 5]);

(
SynthDef(\bell, {
    arg freq=440, amp=1, gate=0, decay = 1, freqs = #[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], rings = #[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], atk = 5, sus = 8, rel = 5;
    var env, sig;
	freqs = {2000.0.rrand(100)}.dup(12);
	rings = {0.1.rrand(2)}.dup(12);
	//env = EnvGen.kr(Env.linen(atk, sus, rel, 1, 4), doneAction: Done.freeSelf);
	env = EnvGen.ar(Env.perc(attackTime:0.01, releaseTime:decay), doneAction: Done.freeSelf);
	sig = Decay.ar(Impulse.ar(0.1), 0.0, ClipNoise.ar(0.01));
	sig = Klank.ar(`[freqs, nil, rings], sig)*env;
	Out.ar(0, [sig, sig]);
}).add;
)


x = Synth(\bell, [\freq, 660, \amp, 0.4]);


x = Synth(\trigger, [\freq, 660, \amp, 0.4]);
x.set(\gate,1);

x.set(\gate, 0);


(
play({
    Klank.ar(`[
        [1, 1071/800, 1253/800, 1723/800]*300,         // frequencies
        nil,                             // amplitudes (default to 1.0)
        [1, 1, 1, 1]               // ring times
        ], Decay.ar(Impulse.ar(4), 0.01, ClipNoise.ar(0.1)))
})
)
