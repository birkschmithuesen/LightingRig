# LightingRig
A tool to process position tracking data and send it to MagicQ/Chamsys

## Description
* die Positionierung der Movingheads und die Berechnung der Pan/Tilt Werte für die “PointAt” Funktion soll im TD Patch “LightingRig” passieren.
* In dem LightingRig soll es dann eine Cue-List geben, die das Verhalten definiert (welche Lampe leuchtet auf welche Performer*in, etc..). Alle weiteren Werte (Helligkeit, Farbe, etc…) werden von MQ festgelegt
* Das LightingRig empfängt alle interessanten Daten vom TD-Main Patch (Bewegungsgeschwindigkeit, Gyroskopdaten, etc…) und kann sie nach Bedarf an MQ weiter leiten, um sie in MQ als Steuerparameter für das Lichtdesign zu nutzen
