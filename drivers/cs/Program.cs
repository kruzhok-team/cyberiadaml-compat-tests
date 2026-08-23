// ----------------------------------------------------------------------------
// The CyberiadaML-GraphML standard compatibility tests
//
// The cyberiada-logic-unity-pkg driver: library round-trip
//
// Copyright (C) 2026 Alexey Fedoseev <aleksey@fedoseev.net>
//
// This program is free software: you can redistribute it and/or
// modify it under the terms of the GNU General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see https://www.gnu.org/licenses/
//
// ----------------------------------------------------------------------------

using System;
using System.Xml;
using Talent.Graphs;

static class Program
{
    static int Main(string[] args)
    {
        if (args.Length != 2)
        {
            Console.Error.WriteLine("usage: CgmlDriver IN.graphml OUT.graphml");
            return 64;
        }
        var converter = new CyberiadaGraphMLConverter("", "");
        try
        {
            converter.SerializeToFile(converter.DeserializeFromFile(args[0]),
                                      args[1]);
        }
        catch (XmlException error)
        {
            Console.Error.WriteLine("rejected by cyberiada-logic-unity-pkg: "
                                    + error.Message);
            return 2;
        }
        // any other exception propagates: a crash verdict for the harness
        return 0;
    }
}
