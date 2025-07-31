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

SynthDef(\bell, {
    arg freq=440, amp=0.2, pan=0;
    var env, sig, overtone, shimmer, delay;
    overtone = SinOsc.ar(freq * 2, 0, 0.2) + SinOsc.ar(freq * 3, 0, 0.1);
    shimmer = HPF.ar(WhiteNoise.ar(0.1), freq * 2) * EnvGen.kr(Env.perc(0.01, 0.3));
    sig = SinOsc.ar(freq) * 0.4 + overtone + shimmer;
    env = EnvGen.kr(Env.perc(0.01, 1), doneAction: 2); // fast attack, 1s decay
    //delay = CombN.ar(sig, 0.2, 0.1, 1.5) * 0.2;
    sig = (sig * env * amp) + (DelayN.ar(sig, 0.1, 0.1).tanh * 0.2);// + delay;
    Out.ar(0, Pan2.ar(sig, pan));
}).add;

x = Synth(\bell, [\freq, 660, \amp, 0.4]);
x.set(\gate, 0);