#include "JRTransport/Version.h"
#include "JRTransport/World.h"
#include <boost/program_options.hpp>
#include <iostream>

namespace po = boost::program_options;

int main(int argc, char* argv[])
{
    // Arguments parsing
    po::variables_map vm;
    po::options_description desc("Allowed options");
    desc.add_options()("help,h", "Produce help message.")("version,v", "Show program name/version banner and exit.")(
        "rev", "Print the SVN revision number");
    po::store(parse_command_line(argc, argv, desc), vm);
    po::notify(vm);
    // help
    if (vm.count("help")) {
        std::cout << desc << std::endl;
        return EXIT_SUCCESS;
    }
    // version
    if (vm.count("version")) {
        std::cout << "HelloRunner version " << JollyRoger::JRTransport::Version::getString() << std::endl;
        return EXIT_SUCCESS;
    }
    // rev
    if (vm.count("rev")) {
        std::cout << "SVN revision : " << JollyRoger::JRTransport::Version::getRevision() << std::endl;
        return EXIT_SUCCESS;
    }

    // Actual "work"
    JollyRoger::JRTransport::World hello;
    hello.greet();

    return EXIT_SUCCESS;
}
