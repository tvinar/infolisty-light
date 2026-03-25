#! /usr/bin/perl -w
use strict;

my $csvlink = "https://docs.google.com/spreadsheets/d/1aK9Bz5WjUNF2fmn3NDKYCH-UREWvNmvs-LYeFl-xouY/export?format=tsv";

open IN, "wget -O - $csvlink |";

while (my $line = <IN>) {
    chomp $line;
    my @parts = split "\t", $line;
    print $parts[1],"\n" unless
	($parts[1] eq "" || $parts[1] eq "skratka" || $parts[1] =~ /tmp/);
}
