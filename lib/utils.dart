String getTypeDescription(int typeNumber) {
  switch (typeNumber) {
    case 0:
      return "Not available";
    case 1:
    case 2:
    case 3:
    case 4:
    case 5:
    case 6:
    case 7:
    case 8:
    case 9:
    case 10:
    case 11:
    case 12:
    case 13:
    case 14:
    case 15:
    case 16:
    case 17:
    case 18:
    case 19:
      return "Reserved for future use";
    case 20:
      return "Wing in ground (WIG), all ships of this type";
    case 21:
      return "Wing in ground (WIG), Hazardous category A";
    case 22:
      return "Wing in ground (WIG), Hazardous category B";
    case 23:
      return "Wing in ground (WIG), Hazardous category C";
    case 24:
      return "Wing in ground (WIG), Hazardous category D";
    case 25:
    case 26:
    case 27:
    case 28:
    case 29:
      return "Wing in ground (WIG), Reserved for future use";
    case 30:
      return "Fishing";
    case 31:
      return "Towing";
    case 32:
      return "Towing: length exceeds 200m or breadth exceeds 25m";
    case 33:
      return "Dredging or underwater ops";
    case 34:
      return "Diving ops";
    case 35:
      return "Military ops";
    case 36:
      return "Sailing";
    case 37:
      return "Pleasure Craft";
    case 38:
    case 39:
      return "Reserved";
    case 40:
      return "High speed craft (HSC), all ships of this type";
    case 41:
      return "High speed craft (HSC), Hazardous category A";
    case 42:
      return "High speed craft (HSC), Hazardous category B";
    case 43:
      return "High speed craft (HSC), Hazardous category C";
    case 44:
      return "High speed craft (HSC), Hazardous category D";
    case 45:
    case 46:
    case 47:
    case 48:
      return "High speed craft (HSC), Reserved for future use";
    case 49:
      return "High speed craft (HSC), No additional information";
    case 50:
      return "Pilot Vessel";
    case 51:
      return "Search and Rescue vessel";
    case 52:
      return "Tug";
    case 53:
      return "Port Tender";
    case 54:
      return "Anti-pollution equipment";
    case 55:
      return "Law Enforcement";
    case 56:
    case 57:
      return "Spare - Local Vessel";
    case 58:
      return "Medical Transport";
    case 59:
      return "Noncombatant ship according to RR Resolution No. 18";
    case 60:
      return "Passenger, all ships of this type";
    case 61:
      return "Passenger, Hazardous category A";
    case 62:
      return "Passenger, Hazardous category B";
    case 63:
      return "Passenger, Hazardous category C";
    case 64:
      return "Passenger, Hazardous category D";
    case 65:
    case 66:
    case 67:
    case 68:
      return "Passenger, Reserved for future use";
    case 69:
      return "Passenger, No additional information";
    case 70:
      return "Cargo, all ships of this type";
    case 71:
      return "Cargo, Hazardous category A";
    case 72:
      return "Cargo, Hazardous category B";
    case 73:
      return "Cargo, Hazardous category C";
    case 74:
      return "Cargo, Hazardous category D";
    case 75:
    case 76:
    case 77:
    case 78:
      return "Cargo, Reserved for future use";
    case 79:
      return "Cargo, No additional information";
    case 80:
      return "Tanker, all ships of this type";
    case 81:
      return "Tanker, Hazardous category A";
    case 82:
      return "Tanker, Hazardous category B";
    case 83:
      return "Tanker, Hazardous category C";
    case 84:
      return "Tanker, Hazardous category D";
    case 85:
    case 86:
    case 87:
    case 88:
      return "Tanker, Reserved for future use";
    case 89:
      return "Tanker, No additional information";
    case 90:
      return "Other Type, all ships of this type";
    case 91:
      return "Other Type, Hazardous category A";
    case 92:
      return "Other Type, Hazardous category B";
    case 93:
      return "Other Type, Hazardous category C";
    case 94:
      return "Other Type, Hazardous category D";
    case 95:
    case 96:
    case 97:
    case 98:
      return "Other Type, Reserved for future use";
    case 99:
      return "Other Type, No additional information";
    default:
      return "Unknown type";
  }
}


 String getStatusDescription(int statusNumber) {
    switch (statusNumber) {
      case 0:
        return "Underway using engine";
      case 1:
        return "At anchor";
      case 2:
        return "Not under command";
      case 3:
        return "Restricted maneuverability";
      case 4:
        return "Constrained by her draught";
      case 5:
        return "Moored";
      case 6:
        return "Aground";
      case 7:
        return "Engaged in fishing";
      case 8:
        return "Underway sailing";
      case 9:
        return "Reserved for future amendment (DG, HS, HSC)";
      case 10:
        return "Reserved for future use (pollutants)";
      case 11:
        return "Power-driven vessel towing astern";
      case 12:
        return "Power-driven vessel pushing ahead or towing alongside";
      case 13:
        return "Reserved for future use";
      case 14:
        return "AIS-SART Active (Search and Rescue)";
      case 15:
        return "Undefined";
      default:
        return "Unknown status";
    }
  }