
(
///////////////////////////////////
// setup
///////////////////////////////////
~numLights = 16;


///////////////////////////////////
// Synth Def
///////////////////////////////////

SynthDef(\base, {
	arg freq = 200, detune = 1.01, amp = 0.1, tremolo = 10, exc = 1.0;
	var sig;
	//tremolo = In.kr(~tilt_degree).linlin(0,1,5,100);
	//detune = In.kr(~pan_degree).linlin(0,1,1.01,2.0);
	//amp = In.kr(~tilt_speed);
	//tremolo = MouseY.kr(5, 200, 1);
	amp = (0.5 + SinOsc.kr(tremolo * 0.5)) * amp;
	//detune = MouseY.kr(1.01, 2.0);
	//amp = Saw.kr({ExpRand(1,3)}!2).range(0.2, 1) * amp;
	sig = Mix.ar({LFPulse.ar(freq * Rand(-1.0, 1.0).range(detune.reciprocal, detune))}!4);
	sig = sig * amp * exc;
	Out.ar(0, sig.dup(2));
}).add;



///////////////////////////////////
// Synth section
///////////////////////////////////

~numLights.do{
	arg i;
	~synths[i].free;Synth.new(\base)}!~numLights;
~synths = {arg i; Synth.new(\base)}!~numLights;

)


s.plotTree;

~synths[2].set(\exc, 0);

(
~numLights.do{
	arg i;
	~synths[i].set(\exc, 0);
}
)

///////////////////////////////////
// receive the OSC information
///////////////////////////////////

(
OSCFunc({
	arg msg;
	var val;
	//msg.postln;
	~numLights.do{
		arg i;
		~synths[i].set(\exc, msg[i+1]);
	}
	//~tilt_degree.value = msg[1].linlin(-10.0, 10.0, 0, 1).postln;
	//~pan_degree.value = msg[2].linlin(-10.0, 10.0, 0, 1);
},
('/vel')
);
)









)


/////////////////////////////////////////


(
a = {
	arg freq = 1, amp = 0.1;
	var sig;
	freq = 100 + (freq * 1000);
	sig = Saw.ar(freq, amp);
	Out.ar(0,[sig, sig]);
}.play;
)


a.set(\freq, 0.1);


a.map(1, ~tilt_degree);


/////////////////////////////////////////

(
// something to play with
SynthDef(\help_Bus, { arg out=0,ffreq=100;
    var x;
    x = RLPF.ar(LFPulse.ar(SinOsc.kr(0.2, 0, 10, 21), [0,0.1], 0.1),
            ffreq, 0.1)
            .clip2(0.4);
    Out.ar(out, x);
}).add;

)

x = Synth(\help_Bus);


